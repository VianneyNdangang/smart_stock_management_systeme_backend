class PermissionCodes:

    # USERS

    VIEW_USERS = "users.view_user"
    CREATE_USERS = "users.add_user"
    UPDATE_USERS = "users.change_user"
    DELETE_USERS = "users.delete_user"


    # GROUPS

    VIEW_GROUPS = "auth.view_group"
    CREATE_GROUPS = "auth.add_group"
    UPDATE_GROUPS = "auth.change_group"
    DELETE_GROUPS = "auth.delete_group"


    # PERMISSIONS

    VIEW_PERMISSIONS = "auth.view_permission"


    # WAREHOUSES

    VIEW_WAREHOUSES = "warehouses.view_warehouse"
    CREATE_WAREHOUSES = "warehouses.add_warehouse"
    UPDATE_WAREHOUSES = "warehouses.change_warehouse"
    DELETE_WAREHOUSES = "warehouses.delete_warehouse"


    # PRODUCTS

    VIEW_PRODUCTS = "products.view_product"
    CREATE_PRODUCTS = "products.add_product"
    UPDATE_PRODUCTS = "products.change_product"
    DELETE_PRODUCTS = "products.delete_product"


    # ATTRIBUTES

    VIEW_ATTRIBUTES = "attributes.view_attribute"
    CREATE_ATTRIBUTES = "attributes.add_attribute"
    UPDATE_ATTRIBUTES = "attributes.change_attribute"
    DELETE_ATTRIBUTES = "attributes.delete_attribute"


    # Attribute values

    VIEW_ATTRIBUTE_VALUES = "products.view_attributevalue"
    CREATE_ATTRIBUTE_VALUES = "products.add_attributevalue"
    UPDATE_ATTRIBUTE_VALUES = "products.change_attributevalue"


    # Variants
    
    VIEW_VARIANTS = "products.view_variant"
    CREATE_VARIANTS = "products.add_variant"
    UPDATE_VARIANTS = "products.change_variant"
    DELETE_VARIANTS = "products.delete_variant"

    # CATEGORIES

    VIEW_CATEGORIES = "categories.view_category"
    CREATE_CATEGORIES = "categories.add_category"
    UPDATE_CATEGORIES = "categories.change_category"
    DELETE_CATEGORIES = "categories.delete_category"


    # INVENTORY

    VIEW_INVENTORY = "inventory.view_stock"
    CREATE_INVENTORY = "inventory.add_stock"
    UPDATE_INVENTORY = "inventory.change_stock"
    DELETE_INVENTORY = "inventory.delete_stock"

    VIEW_STOCK_MOVEMENTS = "inventory.view_stockmovement"
    CREATE_STOCK_MOVEMENTS = "inventory.add_stockmovement"
    UPDATE_STOCK_MOVEMENTS = "inventory.change_stockmovement"
    DELETE_STOCK_MOVEMENTS = "inventory.delete_stockmovement"


    # PURCHASES

    VIEW_PURCHASES = "purchases.view_purchase"
    CREATE_PURCHASES = "purchases.add_purchase"
    UPDATE_PURCHASES = "purchases.change_purchase"
    DELETE_PURCHASES = "purchases.delete_purchase"


    # SALES

    VIEW_SALES = "sales.view_sale"
    CREATE_SALES = "sales.add_sale"
    UPDATE_SALES = "sales.change_sale"
    DELETE_SALES = "sales.delete_sale"


    # ALERTS

    VIEW_ALERTS = "alerts.view_alert"
    CREATE_ALERTS = "alerts.add_alert"
    UPDATE_ALERTS = "alerts.change_alert"
    DELETE_ALERTS = "alerts.delete_alert"


    # PREDICTIONS

    VIEW_PREDICTIONS = "predictions.view_prediction"
    CREATE_PREDICTIONS = "predictions.add_prediction"
    UPDATE_PREDICTIONS = "predictions.change_prediction"
    DELETE_PREDICTIONS = "predictions.delete_prediction"


    # DASHBOARD

    VIEW_DASHBOARD = "dashboard.view_dashboard"