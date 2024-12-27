# 创建安装工人代理（使用轨道长度）
import importlib
from swarm import Agent
from swarm.core import Result

def calculate_installation_cost_by_rail_length(length: int, curtain_type: str = '定制普通窗帘', worker_name: str = None, context_variables: dict = None):
    """
    计算窗帘安装的人工成本，基于轨道的长度。

    Args:
        length (int): 轨道的长度，单位为毫米。
        curtain_type (str, optional): 窗帘类型，例如 '定制普通窗帘'、'定制电动窗帘'、'成品帘'，默认为 '定制普通窗帘'。
        worker_name (str, optional): 工人名称，用于动态加载安装工人计算公式。
        context_variables (dict, optional): 上下文变量。

    Returns:
        Result: 包含返回值、代理和上下文变量的 Result 对象。
    """
    if context_variables is None:
        context_variables = {}

    if worker_name is None:
        return "缺少工人信息，无法计算安装成本。"

    # 将长度转换为米
    length_m = length / 1000

    try:
        # 动态加载工人模块
        worker_module = importlib.import_module(f"workers.installation.{worker_name}")
    except ImportError:
        return Result(
            value={"error": f"无法找到工人 '{worker_name}' 的安装计算模块。"},
            agent=None,
            context_variables={}
        )

    try:
        # 调用工人特定的计算函数，返回 Result 对象
        result = worker_module.calculate_installation_cost(length_m, curtain_type)
    except AttributeError:
        return Result(
            value={"error": f"工人 '{worker_name}' 的模块中缺少 'calculate_installation_cost' 函数。"},
            agent=None,
            context_variables={}
        )

    # 检查返回的是否是 Result 对象
    if isinstance(result, Result):
        return result
    else:
        # 如果工人计算函数未返回 Result 对象，手动创建
        return Result(
            value=result,
            agent=None,
            context_variables={}
        )

installation_agent = Agent(
    name="安装工人代理",
    instructions="""
您是一个专业的窗帘安装工人费用计算专家。请根据用户的自然语言描述，提取以下参数：

- 轨道的长度（length），单位为毫米。
- 窗帘类型（curtain_type），例如 '定制普通窗帘'、'定制电动窗帘'、'成品帘'。
- 工人名称（worker_name），例如 'zhangsan'。

请确保准确提取上述参数，并调用相应的函数进行计算。
""",
    functions=[calculate_installation_cost_by_rail_length],
)
