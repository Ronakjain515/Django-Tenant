from tenants.models import Client, Domain

# create your public tenant
tenant = Client(schema_name="public", name="Schemas Inc.")
tenant.save()

# Add one or more domains for the tenant
domain = Domain()
domain.domain = "localhost"
domain.tenant = tenant
domain.is_primary = True
domain.save()


# create your first real tenant
tenant = Client(schema_name="healthlink", name="HealthLink Inc.")
tenant.save()  # migrate_schemas automatically called, your tenant is ready to be used!

# Add one or more domains for the tenant
domain = Domain()
domain.domain = "healthlink"
domain.tenant = tenant
domain.is_primary = True
domain.save()
