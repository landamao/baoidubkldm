from astrbot.api.all import *; from astrbot.api.event import AstrMessageEvent; import html, random

try: import requests, aiohttp
except ImportError:
    logger.error("模块导入失败，正在为你安装模块")
    try:
        import subprocess, sys, importlib
        subprocess.check_call([ sys.executable, "-m", "pip", "install", "requests", "aiohttp",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "--trusted-host", "pypi.tuna.tsinghua.edu.cn"])
        importlib.invalidate_caches()
        import requests, aiohttp; del subprocess, sys, importlib
        logger.error("模块导入成功")
    except Exception as e: logger.error(f"导入模块发生错误:\n{e}", exc_info=True); raise ImportError
except Exception as e: logger.error(f"导入模块发生错误:\n{e}", exc_info=True); raise RuntimeError

@register("百度百科插件", "懒大猫", "百度百科插件", "6.6.6")
class 百度百科(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.l用户代理池 = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Edge/121.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        logger.info("百度百科插件加载完成")

    async def f(self, 查询词条: str) -> str:
        api地址 = "https://oiapi.net/api/BaiduEncyclopedia"; 参数 = {"msg": 查询词条}
        代理 = random.choice(self.l用户代理池)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get( url=api地址, params=参数, headers={
                            "User-Agent": 代理},
                            timeout=aiohttp.ClientTimeout(total=10)
                ) as 响应:
                    响应.raise_for_status(); 接口数据 = await 响应.json()
                    if not 接口数据.get("data"):  return f"「{查询词条}」百度百科暂未收录该词条"
                    data = 接口数据["data"]
                    搜索词条名 = html.unescape(data.get("search", "未知词条"))
                    词条简介 = html.unescape(data.get("result", "无简介"))
                    百科链接 = html.unescape(data.get("url", "无详情页链接"))

                    最大字数 = 600; 简介 = 词条简介[:最大字数] + "..." if len(词条简介) > 最大字数 else 词条简介

                    return f"搜索词条：{搜索词条名}\n\n{简介}\n\n详情页：{百科链接}"

        except asyncio.TimeoutError:  return "请求超时"
        except aiohttp.ClientError as e:  logger.error(f"网络请求错误：\n{e}"); return "搜索失败"
        except Exception as e:  logger.error(f"搜索失败：\n{e}", exc_info=True); return "搜索失败"

    @event_message_type(EventMessageType.GROUP_MESSAGE,priority=99)
    async def g(self, event: AstrMessageEvent):
        v消息文本内容 = event.message_str
        if v消息文本内容.startswith("百度百科") and len(v消息文本内容) > 4:
            event.stop_event(); 搜索词条 = v消息文本内容[4:].strip()
            if len(搜索词条) > 30:  yield event.plain_result("词条过长"); return
            if 搜索词条:  百科结果 = await self.f(搜索词条); yield event.plain_result(百科结果)
        return
