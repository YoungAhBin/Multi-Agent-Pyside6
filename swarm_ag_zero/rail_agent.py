# 创建轨道代理
import importlib
from swarm import Agent
from swarm.core import Result

def calculate_rail_cost_agent(length: int, rail_type: str = '普通轨道', manufacturer: str = None, context_variables: dict = None):
    """
    计算窗帘的轨道成本，动态调用厂家计算公式。

    Args:
        length (int): 轨道的长度，单位为毫米。
        rail_type (str, optional): 轨道类型，例如 '普通轨道'、'电动轨道' 等，默认为 '普通轨道'。
        manufacturer (str, optional): 厂家名称，用于动态加载计算公式。
        context_variables (dict, optional): 上下文变量。

    Returns:
        Result: 包含返回值、代理和上下文变量的 Result 对象。
    """
    if context_variables is None:
        context_variables = {}

    if manufacturer is None:
        return "缺少厂家信息，无法计算轨道成本。"

    # 将长度转换为米
    length_m = length / 1000

    try:
        # 动态加载厂家模块
        manufacturer_module = importlib.import_module(f"manufacturers.rails.{manufacturer}")
    except ImportError:
        return Result(
            value={"error": f"无法找到厂家 '{manufacturer}' 的计算模块。"},
            agent=None,
            context_variables={}
        )

    try:
        # 调用厂家特定的计算函数，返回 Result 对象
        result = manufacturer_module.calculate_rail_cost(length_m, rail_type)
    except AttributeError:
        return Result(
            value={"error": f"厂家 '{manufacturer}' 的模块中缺少 'calculate_rail_cost' 函数。"},
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

rail_agent = Agent(
    name="轨道计算代理",
    instructions="""
您是一个专业的轨道成本计算专家。请根据用户的自然语言描述，提取以下参数：

- 轨道的长度（length），单位为毫米。
- 轨道的类型（rail_type），例如 '普通轨道'、'电动轨道' 等。
- 厂家名称（manufacturer），例如 'tongshun'。

请确保准确提取上述参数，并调用相应的函数进行计算。
""",
    functions=[calculate_rail_cost_agent],
)
