"""Pulumi infrastructure for Humanoid Robot Insurance Platform."""

import pulumi
import pulumi_azure_native as azure_native
from pulumi import Config, Output

# Configuration
config = Config()
app_name = "humanoid-robot-insurance"
environment = config.get("environment") or "dev"
location = config.get("azure-native:region") or "East US"
postgres_admin_login = config.get("postgresAdminLogin") or "adminuser"
postgres_admin_password = config.require_secret("postgresAdminPassword")

# Resource naming
resource_prefix = f"{app_name}-{environment}"
container_app_name = f"{resource_prefix}-app"
container_registry_name = resource_prefix.replace("-", "") + "acr"
postgres_server_name = f"{resource_prefix}-postgres"
key_vault_name = f"{resource_prefix}-kv"
log_analytics_name = f"{resource_prefix}-logs"
app_insights_name = f"{resource_prefix}-insights"
container_app_env_name = f"{resource_prefix}-env"

# Resource Group
resource_group = azure_native.resources.ResourceGroup(
    "rg",
    resource_group_name=f"rg-{resource_prefix}",
    location=location
)

# Log Analytics Workspace
log_analytics = azure_native.operationalinsights.Workspace(
    "log-analytics",
    resource_group_name=resource_group.name,
    workspace_name=log_analytics_name,
    location=location,
    sku=azure_native.operationalinsights.WorkspaceSkuArgs(
        name="PerGB2018"
    ),
    retention_in_days=30
)

# Application Insights
app_insights = azure_native.insights.Component(
    "app-insights",
    resource_group_name=resource_group.name,
    resource_name=app_insights_name,
    location=location,
    kind="web",
    application_type="web",
    workspace_resource_id=log_analytics.id
)

# Container Registry
container_registry = azure_native.containerregistry.Registry(
    "container-registry",
    resource_group_name=resource_group.name,
    registry_name=container_registry_name,
    location=location,
    sku=azure_native.containerregistry.SkuArgs(
        name="Basic"
    ),
    admin_user_enabled=True
)

# PostgreSQL Flexible Server
postgres_server = azure_native.dbforpostgresql.Server(
    "postgres-server",
    resource_group_name=resource_group.name,
    server_name=postgres_server_name,
    location=location,
    sku=azure_native.dbforpostgresql.SkuArgs(
        name="Standard_B1ms",
        tier="Burstable"
    ),
    administrator_login=postgres_admin_login,
    administrator_login_password=postgres_admin_password,
    version="15",
    storage=azure_native.dbforpostgresql.StorageArgs(
        storage_size_gb=32
    ),
    backup=azure_native.dbforpostgresql.BackupArgs(
        backup_retention_days=7,
        geo_redundant_backup="Disabled"
    ),
    high_availability=azure_native.dbforpostgresql.HighAvailabilityArgs(
        mode="Disabled"
    )
)

# PostgreSQL Database
postgres_database = azure_native.dbforpostgresql.Database(
    "postgres-database",
    resource_group_name=resource_group.name,
    server_name=postgres_server.name,
    database_name="humanoid_robot_insurance",
    charset="UTF8",
    collation="en_US.UTF8"
)

# PostgreSQL Firewall Rule (Allow Azure Services)
postgres_firewall_rule = azure_native.dbforpostgresql.FirewallRule(
    "postgres-firewall-rule",
    resource_group_name=resource_group.name,
    server_name=postgres_server.name,
    firewall_rule_name="AllowAzureServices",
    start_ip_address="0.0.0.0",
    end_ip_address="0.0.0.0"
)

# Key Vault
key_vault = azure_native.keyvault.Vault(
    "key-vault",
    resource_group_name=resource_group.name,
    vault_name=key_vault_name,
    location=location,
    properties=azure_native.keyvault.VaultPropertiesArgs(
        sku=azure_native.keyvault.SkuArgs(
            family="A",
            name="standard"
        ),
        tenant_id=azure_native.authorization.get_client_config().tenant_id,
        access_policies=[],
        enable_rbac_authorization=True
    )
)

# Container Apps Environment
container_app_env = azure_native.app.ManagedEnvironment(
    "container-app-env",
    resource_group_name=resource_group.name,
    environment_name=container_app_env_name,
    location=location,
    app_logs_configuration=azure_native.app.AppLogsConfigurationArgs(
        destination="log-analytics",
        log_analytics_configuration=azure_native.app.LogAnalyticsConfigurationArgs(
            customer_id=log_analytics.customer_id,
            shared_key=log_analytics.get_shared_keys().apply(lambda keys: keys.primary_shared_key)
        )
    )
)

# Container App
container_app = azure_native.app.ContainerApp(
    "container-app",
    resource_group_name=resource_group.name,
    container_app_name=container_app_name,
    location=location,
    managed_environment_id=container_app_env.id,
    configuration=azure_native.app.ConfigurationArgs(
        ingress=azure_native.app.IngressArgs(
            external=True,
            target_port=8000,
            allow_insecure=False,
            traffic=[
                azure_native.app.TrafficWeightArgs(
                    latest_revision=True,
                    weight=100
                )
            ]
        ),
        secrets=[
            azure_native.app.SecretArgs(
                name="database-url",
                value=Output.concat(
                    "postgresql://",
                    postgres_admin_login,
                    ":",
                    postgres_admin_password,
                    "@",
                    postgres_server.fully_qualified_domain_name,
                    ":5432/humanoid_robot_insurance"
                )
            ),
            azure_native.app.SecretArgs(
                name="secret-key",
                value="your-secret-key-here"  # This should be generated or provided securely
            ),
            azure_native.app.SecretArgs(
                name="keyvault-url",
                value=key_vault.properties.apply(lambda props: props.vault_uri)
            ),
            azure_native.app.SecretArgs(
                name="app-insights-connection-string",
                value=app_insights.connection_string
            )
        ],
        registries=[
            azure_native.app.RegistryCredentialsArgs(
                server=container_registry.login_server,
                username=container_registry.name,
                password_secret_ref="registry-password"
            )
        ]
    ),
    template=azure_native.app.TemplateArgs(
        containers=[
            azure_native.app.ContainerArgs(
                name="humanoid-robot-insurance",
                image=Output.concat(
                    container_registry.login_server,
                    "/humanoid-robot-insurance:latest"
                ),
                resources=azure_native.app.ContainerResourcesArgs(
                    cpu=0.5,
                    memory="1Gi"
                ),
                env=[
                    azure_native.app.EnvironmentVarArgs(
                        name="DATABASE_URL",
                        secret_ref="database-url"
                    ),
                    azure_native.app.EnvironmentVarArgs(
                        name="SECRET_KEY",
                        secret_ref="secret-key"
                    ),
                    azure_native.app.EnvironmentVarArgs(
                        name="AZURE_KEYVAULT_URL",
                        secret_ref="keyvault-url"
                    ),
                    azure_native.app.EnvironmentVarArgs(
                        name="AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING",
                        secret_ref="app-insights-connection-string"
                    ),
                    azure_native.app.EnvironmentVarArgs(
                        name="ENVIRONMENT",
                        value=environment
                    )
                ],
                probes=[
                    azure_native.app.ContainerAppProbeArgs(
                        type="Liveness",
                        http_get=azure_native.app.ContainerAppProbeHttpGetArgs(
                            path="/health",
                            port=8000
                        ),
                        initial_delay_seconds=30,
                        period_seconds=30
                    ),
                    azure_native.app.ContainerAppProbeArgs(
                        type="Readiness",
                        http_get=azure_native.app.ContainerAppProbeHttpGetArgs(
                            path="/health",
                            port=8000
                        ),
                        initial_delay_seconds=5,
                        period_seconds=10
                    )
                ]
            )
        ],
        scale=azure_native.app.ScaleArgs(
            min_replicas=1,
            max_replicas=10,
            rules=[
                azure_native.app.ScaleRuleArgs(
                    name="http-scaling",
                    http=azure_native.app.HttpScaleRuleArgs(
                        metadata={
                            "concurrentRequests": "10"
                        }
                    )
                )
            ]
        )
    )
)

# Exports
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("container_app_url", Output.concat("https://", container_app.configuration.apply(lambda config: config.ingress.fqdn)))
pulumi.export("container_registry_login_server", container_registry.login_server)
pulumi.export("postgres_server_fqdn", postgres_server.fully_qualified_domain_name)
pulumi.export("key_vault_uri", key_vault.properties.apply(lambda props: props.vault_uri))
pulumi.export("app_insights_connection_string", app_insights.connection_string)