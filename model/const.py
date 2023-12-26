class OrderStatus:
    Open = 'open'  # 订单正在执行
    Canceled = 'canceled'  # 订单已被取消
    PendingCancel = 'pending_cancel'  # 订单正在等待取消
    PendingNew = 'pending_new'  # 订单正在等待创建
    PendingFill = 'pending_fill'  # 订单正在等待成交

    Closed = 'closed'  # 订单已结束, 无论是成功还是失败
    Filled = 'FILLED'  # 订单已完全成交

