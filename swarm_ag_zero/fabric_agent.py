# 创建布料代理
import importlib
from swarm import Agent
from swarm.core import Result

def calculate_fabric_cost_agent(width: int, height: int, curtain_type: str = '纱帘', manufacturer: str = None, fabric_model: str = None, context_variables: dict = None):
    """
    计算窗帘的布料成本，动态调用厂家计算公式，并返回多个值。

    Args:
        width (int): 窗帘的宽度，单位为毫米。
        height (int): 窗帘的高度，单位为毫米。
        curtain_type (str, optional): 窗帘类型，例如 '纱帘'、'遮光帘' 等，默认为 '纱帘'。
        manufacturer (str, optional): 厂家名称，用于动态加载计算公式。
        fabric_model (str, optional): 面料型号，用于动态获取面料价格。
        context_variables (dict, optional): 上下文变量。

    Returns:
        Result: 包含返回值、代理和上下文变量的 Result 对象。
    """
    if context_variables is None:
        context_variables = {}

    if manufacturer is None:
        return "缺少厂家信息，无法计算布料成本。"

    # 将尺寸转换为米
    width_m = width / 1000
    height_m = height / 1000

    try:
        # 动态加载厂家模块
        manufacturer_module = importlib.import_module(f"manufacturers.fabrics.{manufacturer}")
    except ImportError:
        return Result(
            value={"error": f"无法找到厂家 '{manufacturer}' 的计算模块。"},
            agent=None,
            context_variables={}
        )

    try:
        # 调用厂家特定的计算函数，返回 Result 对象
        result = manufacturer_module.calculate_fabric_cost(width_m, height_m, curtain_type, fabric_model)
    except AttributeError:
        return Result(
            value={"error": f"厂家 '{manufacturer}' 的模块中缺少 'calculate_fabric_cost' 函数。"},
            agent=None,
            context_variables={}
        )

    # 检查返回的是否是 Result 对象
    if isinstance(result, Result):
        return result
    else:
        # 如果厂家计算函数未返回 Result 对象，手动创建
        return Result(
            value=result,
            agent=None,
            context_variables={}
        )

fabric_agent = Agent(
    name="面料计算代理",
    instructions="""
您是一个专业的布料成本计算专家。请根据用户的自然语言描述，提取以下参数：

- 窗帘的宽度（width），单位为毫米。
- 窗帘的高度（height），单位为毫米。
- 窗帘的类型（curtain_type），例如 '纱帘'、'遮光帘' 等。
- 厂家名称（manufacturer），例如 'mingyuan'。
- 面料型号（fabric_model），例如 '186A素色布'、'色织提花布' 等。

请确保准确提取上述参数，并调用相应的函数进行计算。
""",
    functions=[calculate_fabric_cost_agent],
)
