def audit_record_display(identifier, diff_view):
    from compstack.audit.grids import AuditGrid

    class SimpleAuditGrid(AuditGrid):
        hide_controls_box = True

    return SimpleAuditGrid(identifier=identifier, diff_view=diff_view).html()
