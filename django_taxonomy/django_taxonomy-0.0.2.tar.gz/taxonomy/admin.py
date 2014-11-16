
from mptt.admin import MPTTModelAdmin


class TaxonomyModelAdmin(MPTTModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_display = ["name", "weight", "published", "id"]
    list_editable = ["published", "weight"]
