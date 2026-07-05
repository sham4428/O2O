# O2O 商城自动化脚本

这是一个 Selenium 自动化脚本，用于执行 O2O 商城登录、搜索、下单、支付和查看订单流程。

## 环境

- Python 3.8+
- Chrome 浏览器
- Selenium 4.6+

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## 配置

不要把真实账号、密码或内网地址提交到 GitHub。运行前请通过环境变量配置：

```powershell
$env:O2O_URL = "你的测试环境地址"
$env:O2O_USERNAME = "你的测试账号"
$env:O2O_PASSWORD = "你的测试密码"
$env:O2O_KEYWORD = "搜索关键词"
```

## 运行

```powershell
python .\o2o_mall.py
```

也可以通过命令行参数覆盖环境变量：

```powershell
python .\o2o_mall.py --url "你的测试环境地址" --username "你的测试账号" --password "你的测试密码" --keyword "坐垫"
```

无界面运行：

```powershell
python .\o2o_mall.py --headless
```

## 说明

- 出错时会保存截图到 `o2o_error_screenshot.png`。
- 脚本依赖当前页面结构，页面 DOM 变化后可能需要更新 XPath。
- 仓库中的代码已脱敏，真实 URL、账号和密码请只放在本地环境变量或运行参数里。
