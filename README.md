# 中文口播音频导演 Agent

一个接近专业后期工程师工作流的中文口播音频优化系统。

## 核心原则

- **Minimum Necessary Edit** - 最小必要编辑
- **宁可少剪，不要误剪** - 保留自然度优先
- **原始声音真实性高于一切** - 真人感>完美度

## 功能流程

```
上传音频
  ↓
自动转写 (Whisper Large-v3 + WhisperX)
  ↓
语义分析 (主题、情绪、节奏)
  ↓
情感分析 (强调、思考、情绪)
  ↓
编辑决策生成 (6阶段分析)
  ↓
自动执行剪辑
  ↓
DSP处理 (降噪、压缩、LUFS标准化)
  ↓
质量检查
  ↓
输出最终音频 + 编辑决策JSON + 转写文本
```

## 技术栈

- **Python 3.11+**
- **FastAPI** - Web框架
- **Whisper Large-v3 + WhisperX** - 中文转写与字级时间戳
- **Librosa + Pydub** - 音频处理
- **Pedalboard** - DSP处理
- **PyLoudNorm** - LUFS标准化
- **Gemini / GPT / DeepSeek** - 编辑决策AI
- **PostgreSQL** - 任务存储
- **Redis** - 队列与缓存
- **Docker** - 容器化部署

## 项目结构

```
audio-director-agent/
├── src/
│   ├── core/
│   │   ├── audio_loader.py          # 音频加载与转换
│   │   ├── transcriber.py           # Whisper转写模块
│   │   ├── semantic_analyzer.py     # 语义分析
│   │   ├── emotion_analyzer.py      # 情感分析
│   │   ├── edit_decision_engine.py  # 编辑决策引擎 (6阶段)
│   │   ├── audio_editor.py          # 音频编辑执行
│   │   ├── dsp_processor.py         # DSP处理
│   │   └── quality_checker.py       # 质量检查
│   ├── api/
│   │   ├── routes.py                # FastAPI路由
│   │   ├── models.py                # Pydantic数据模型
│   │   └── tasks.py                 # 异步任务处理
│   ├── db/
│   │   ├── models.py                # 数据库模型
│   │   └── operations.py            # 数据库操作
│   ├── config.py                    # 配置管理
│   └── utils.py                     # 工具函数
├── tests/
│   ├── test_transcriber.py
│   ├── test_semantic_analyzer.py
│   ├── test_edit_decision.py
│   └── test_dsp_processor.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
└── main.py
```

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url>
cd audio-director-agent

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入必要配置

# 5. 初始化数据库
python -m alembic upgrade head

# 6. 启动服务
python main.py
```

## API 示例

### 上传并处理音频

```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "audio=@sample.mp3" \
  -F "strategy=natural" \
  -F "language=zh"
```

### 响应格式

```json
{
  "task_id": "uuid",
  "status": "completed",
  "output": {
    "audio_url": "/outputs/edited_abc123.wav",
    "edits": [
      {
        "type": "remove",
        "reason": "redundant filler",
        "start": 12.34,
        "end": 12.89,
        "risk_level": "low",
        "affects_emotion": false
      }
    ],
    "transcription": {
      "text": "完整转写文本...",
      "segments": [
        {
          "text": "这是一个",
          "start": 0.0,
          "end": 0.5,
          "confidence": 0.98
        }
      ]
    },
    "quality_metrics": {
      "original_lufs": -20.5,
      "edited_lufs": -16.0,
      "noise_level": "low",
      "breath_artifacts": 0
    }
  }
}
```

## 阶段规划

### Phase 1: Core Infrastructure
- ✅ 项目结构与配置
- [ ] 音频加载与转换模块
- [ ] Whisper集成与转写
- [ ] 基础数据库与API

### Phase 2: Analysis Engine
- [ ] 语义分析（6阶段）
- [ ] 情感分析集成
- [ ] 编辑决策引擎

### Phase 3: Audio Processing
- [ ] 音频编辑执行
- [ ] DSP处理与标准化
- [ ] 质量检查

### Phase 4: Optimization & Deployment
- [ ] 性能优化
- [ ] Docker容器化
- [ ] GPU加速支持
- [ ] 生产部署

## 许可证

MIT

## 作者

Audio Director Agent Development Team
