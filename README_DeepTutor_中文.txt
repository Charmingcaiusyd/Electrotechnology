DeepTutor 本机安装说明

1. 安装位置
   D:\Backup\Documents\EC

2. Python 虚拟环境
   D:\Backup\Documents\EC.venv

3. 启动
   双击 D:\Backup\Documents\EC\Start_DeepTutor.bat

4. 停止
   双击 D:\Backup\Documents\EC\Stop_DeepTutor.bat

5. 本机访问地址
   前端: http://127.0.0.1:3782/
   后端: http://127.0.0.1:8001/
   本地 embedding: http://127.0.0.1:8791/

6. DeepSeek 配置
   Provider: DeepSeek official API
   Base URL: https://api.deepseek.com
   Model: deepseek-v4-pro
   配置文件: D:\Backup\Documents\EC\data\user\settings\model_catalog.json

7. API Key 安全录入
   不要把 API Key 发到聊天、GitHub、截图、BAT、README 或日志中。
   在 PowerShell 中运行:
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Backup\Documents\EC\scripts\Set-DeepSeek-API-Key.ps1"
   该脚本会隐藏输入并只写入本机配置文件。

8. 教材知识库
   默认知识库: electrotechnology_practical_study
   教材副本:
   D:\Backup\Documents\EC\data\user\materials\Electrotechnology_Practical_Study_Print_Pack_v04_Refined_Edition.pdf
   知识库索引:
   D:\Backup\Documents\EC\data\knowledge_bases\electrotechnology_practical_study
   当前索引使用本地 FastEmbed 模型 BAAI/bge-small-en-v1.5，384 维，不上传整本 PDF 到第三方 embedding 服务。

9. 教学动画 / 视频链路
   已安装 FFmpeg、MiKTeX 和 DeepTutor math-animator extra。
   验证视频:
   D:\Backup\Documents\EC\tmp\verify_manim\media\videos\VerifyDeepTutorManim\480p15\VerifyDeepTutorManim.mp4

10. 已安装的增强功能
   - 本地 FastEmbed embedding 服务
   - Docling / MarkItDown / PyMuPDF4LLM 文档解析增强
   - RAGAnything / LightRAG 相关依赖
   - TutorBot / partners / Matrix SDK 依赖
   - Manim 教学动画依赖

11. GraphRAG 状态
   GraphRAG 已安装在隔离环境:
   D:\Backup\Documents\EC.graphrag.venv
   它和 LightRAG/RAGAnything 的 pandas/aiofiles 版本要求冲突，因此不放进主 DeepTutor venv。
   主 DeepTutor venv 保持给 Web 应用、教材知识库、教学动画和 LightRAG/RAGAnything 使用。

12. 日志位置
   D:\Backup\Documents\EC\logs
   后端、前端和本地 embedding 服务分别写入独立日志文件。

13. 备份建议
   建议备份:
   D:\Backup\Documents\EC\data\user
   D:\Backup\Documents\EC\data\knowledge_bases
   不需要备份:
   D:\Backup\Documents\EC.venv
   D:\Backup\Documents\EC\data\user\runtime\web

14. 隐私说明
   普通聊天会把你的问题发送给配置的 LLM API。
   使用知识库回答时，被检索出的相关教材片段可能会作为上下文发送给 LLM API。
   PDF 索引阶段使用本地 embedding，不需要把整本教材上传给 embedding 服务。
