# Infrastructure

This directory contains the Pulumi infrastructure as code for the Humanoid Robot Insurance Platform.

## Structure

- `__main__.py` - Main Pulumi program defining Azure resources
- `Pulumi.yaml` - Pulumi project configuration
- `Pulumi.dev.yaml` - Development environment configuration
- `Pulumi.prod.yaml` - Production environment configuration
- `requirements.txt` - Pulumi dependencies

## Setup

1. **Install dependencies**
   ```bash
   cd infrastructure
   pip install -r requirements.txt
   ```

2. **Login to Pulumi**
   ```bash
   pulumi login
   ```

3. **Initialize stack**
   ```bash
   pulumi stack init dev
   ```

4. **Configure secrets**
   ```bash
   pulumi config set --secret app:postgresAdminPassword YourSecurePassword123!
   ```

## Deployment

### Development Environment
```bash
cd infrastructure
pulumi stack select dev
pulumi up
```

### Production Environment
```bash
cd infrastructure
pulumi stack select prod
pulumi config set --secret app:postgresAdminPassword YourProductionPassword123!
pulumi up
```

## Resources Created

- **Resource Group**: Container for all resources
- **Container Registry**: For storing Docker images
- **PostgreSQL Server**: Managed database service
- **Key Vault**: For secrets management
- **Log Analytics**: For monitoring and logging
- **Application Insights**: For application monitoring
- **Container Apps Environment**: Serverless container platform
- **Container App**: The main application deployment

## Outputs

After deployment, the following outputs are available:

- `container_app_url`: The URL of the deployed application
- `container_registry_login_server`: Container registry server URL
- `postgres_server_fqdn`: PostgreSQL server FQDN
- `key_vault_uri`: Key Vault URI
- `app_insights_connection_string`: Application Insights connection string

## Cleanup

To destroy all resources:
```bash
cd infrastructure
pulumi destroy
```