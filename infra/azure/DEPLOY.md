# Déploiement Azure — Enterprise GenAI Platform

## Architecture cible

```
Internet
    │ HTTPS
    ▼
Azure Container Apps (ingress externe)
    │
    ├── Azure Container Registry (images Docker)
    ├── Azure OpenAI             (GPT-4o + embeddings)
    ├── Azure AI Search          (vector store hybride)
    ├── Azure Key Vault          (secrets)
    └── Log Analytics            (logs + métriques)

Auth: Managed Identity — zéro credential stocké dans le code
```

## Prérequis

```bash
# CLI nécessaires
az --version          # Azure CLI >= 2.60
az bicep version      # Bicep CLI (inclus dans az)
docker --version      # Docker >= 24
gh --version          # GitHub CLI (pour CI/CD)

# Login Azure
az login
az account set --subscription "<SUBSCRIPTION_ID>"
```

## Déploiement en 5 étapes

### 1. Créer le Resource Group

```bash
az group create \
  --name rg-genai-prod \
  --location francecentral
```

### 2. Déployer l'infrastructure (Bicep)

```bash
# Génère un JWT secret fort
JWT_SECRET=$(openssl rand -hex 32)

az deployment group create \
  --resource-group rg-genai-prod \
  --template-file infra/azure/main.bicep \
  --parameters environment=prod \
               jwtSecretKey="$JWT_SECRET" \
               openrouterApiKey="$OPENROUTER_API_KEY"
```

Récupérer les outputs :

```bash
az deployment group show \
  --resource-group rg-genai-prod \
  --name main \
  --query properties.outputs
```

### 3. Build et push de l'image Docker

```bash
# Récupérer le login server ACR depuis les outputs
ACR_SERVER=$(az acr list --resource-group rg-genai-prod --query "[0].loginServer" -o tsv)

# Login ACR via Managed Identity (pas de mot de passe)
az acr login --name $ACR_SERVER

# Build multi-platform + push
docker buildx build \
  --platform linux/amd64 \
  --tag $ACR_SERVER/enterprise-genai-platform:latest \
  --push .
```

### 4. Déployer la nouvelle image

```bash
az containerapp update \
  --name genai-prod-api \
  --resource-group rg-genai-prod \
  --image $ACR_SERVER/enterprise-genai-platform:latest
```

### 5. Vérifier le déploiement

```bash
# URL de l'API
az containerapp show \
  --name genai-prod-api \
  --resource-group rg-genai-prod \
  --query properties.configuration.ingress.fqdn -o tsv

# Health check
API_URL=$(az containerapp show \
  --name genai-prod-api \
  --resource-group rg-genai-prod \
  --query "properties.configuration.ingress.fqdn" -o tsv)

curl https://$API_URL/health
```

---

## CI/CD automatisé (GitHub Actions)

Le fichier `.github/workflows/cd.yml` build et push l'image sur chaque push sur `main`.

### Configurer les secrets GitHub

```bash
# Service Principal pour GitHub Actions
SP=$(az ad sp create-for-rbac \
  --name "github-actions-genai" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-genai-prod \
  --json-auth)

gh secret set AZURE_CREDENTIALS --body "$SP" --repo SeydinaBANE/enterprise-genai-platform
gh secret set ACR_LOGIN_SERVER --body "$ACR_SERVER" --repo SeydinaBANE/enterprise-genai-platform
```

Mettre à jour `.github/workflows/cd.yml` pour ajouter le push ACR :

```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}

- name: Build and push to ACR
  run: |
    az acr login --name ${{ secrets.ACR_LOGIN_SERVER }}
    docker build -t ${{ secrets.ACR_LOGIN_SERVER }}/enterprise-genai-platform:${{ github.sha }} .
    docker push ${{ secrets.ACR_LOGIN_SERVER }}/enterprise-genai-platform:${{ github.sha }}

- name: Deploy to Container Apps
  run: |
    az containerapp update \
      --name genai-prod-api \
      --resource-group rg-genai-prod \
      --image ${{ secrets.ACR_LOGIN_SERVER }}/enterprise-genai-platform:${{ github.sha }}
```

---

## Passer d'OpenRouter à Azure OpenAI

Une fois déployé sur Azure, basculer vers Azure OpenAI natif :

```bash
# Dans .env ou variables Container Apps
AZURE_OPENAI_ENDPOINT=https://genai-prod-openai.openai.azure.com/
LLM_MODEL=azure/gpt-4o               # litellm prefix pour Azure OpenAI
EMBEDDING_MODEL=azure/text-embedding-3-small
```

`litellm` supporte Azure OpenAI avec le même code — seul le prefix du modèle change.

---

## Réseau privé (hardening prod)

Pour un environnement sécurisé complet :

```bash
# Créer un VNet
az network vnet create \
  --name vnet-genai-prod \
  --resource-group rg-genai-prod \
  --address-prefixes 10.0.0.0/16

# Container Apps dans le VNet
az containerapp env update \
  --name genai-prod-env \
  --resource-group rg-genai-prod \
  --infrastructure-subnet-resource-id <SUBNET_ID>

# Private Endpoints pour Azure OpenAI et AI Search
az network private-endpoint create \
  --name pe-openai \
  --resource-group rg-genai-prod \
  --vnet-name vnet-genai-prod \
  --subnet default \
  --private-connection-resource-id $(az cognitiveservices account show \
      --name genai-prod-openai --resource-group rg-genai-prod --query id -o tsv) \
  --group-id account \
  --connection-name conn-openai
```

---

## Coût estimé (prod minimal)

| Service | SKU | $/mois estimé |
|---------|-----|---------------|
| Container Apps | 0.5 vCPU / 1 Gi | ~10€ |
| Container Registry | Basic | ~5€ |
| Azure OpenAI | pay-per-token | variable |
| Azure AI Search | Basic | ~75€ |
| Key Vault | Standard | ~5€ |
| Log Analytics | PerGB2018 (5 GB/j) | ~15€ |
| **Total minimal** | | **~110€/mois** |

> Pour un demo / POC, utiliser OpenRouter (pay-per-use) + ChromaDB local réduit le coût à ~15€/mois (Container Apps + Registry uniquement).

---

## Teardown

```bash
az group delete --name rg-genai-prod --yes --no-wait
```
