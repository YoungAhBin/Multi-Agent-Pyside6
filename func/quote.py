# quote.py
from swarm.core import Result
from manufacturers.fabrics.database import get_fabric_price_by_model

def fixed_height_buy_width(width_m, height_m, curtain_type):
    pleat_base = (width_m * 2) / 0.25
    pleat_count = round(pleat_base)
    if pleat_count % 2 != 0:
        pleat_count += 1
    pleats = pleat_count - 2

    if curtain_type == '纱帘':
        main_fabric_quantity = pleats * 0.25 + 0.3
    else:
        main_fabric_quantity = pleats * 0.25 + 0.3 + 0.2

    return main_fabric_quantity

def fixed_width_buy_height(width_m, height_m, curtain_type):
    pleat_base = (width_m * 2) / 0.25
    pleat_count = round(pleat_base)
    if pleat_count % 2 != 0:
        pleat_count += 1
    pleats = pleat_count - 2
    width_count = round((pleats * 0.25 + 0.3) / 2.8)

    if curtain_type == '纱帘':
        main_fabric_quantity = width_count * (height_m + 0.2)
    else:
        main_fabric_quantity = width_count * (height_m + 0.2) + 0.2

    return main_fabric_quantity

def calculate_fabric_cost(width_m, height_m, curtain_type, fabric_model):
    """
    计算布料成本，根据高度选择相应的计算方法。

    Returns:
        Result: 包含成本和主布数量的 Result 对象。
    """
     # 从数据库获取面料价格
    UNIT_PRICE = get_fabric_price_by_model(model_number=fabric_model)

    # 如果没找到价格，则返回错误
    if UNIT_PRICE is None:
        return Result(
            value=f"Error: Could not find price for fabric model '{fabric_model}'",
            agent=None,
            context_variables={}
        )

    if height_m > 2.8:
        main_fabric_quantity = fixed_width_buy_height(width_m, height_m, curtain_type)
    else:
        main_fabric_quantity = fixed_height_buy_width(width_m, height_m, curtain_type)

    cost = main_fabric_quantity * UNIT_PRICE

    # 返回成本和主布数量
    return Result(
        value=f"需要的面料长度是：{main_fabric_quantity} 米，需要面料的费用是 {cost} 元",
        agent=None,
        context_variables={}
    )
