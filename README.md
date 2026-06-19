# VoiceFlow-CN

中文口播音频专业剪辑与自然优化系统

AI 驱动的中文口播自动后期处理系统。

## 项目定位

目标并非创造新的声音，也不是替换配音员或重建音频。

**目标是**：在最大程度保留原始录音真实性的前提下，自动完成专业后期剪辑与自然优化。

## 设计哲学

优先级：
1. 保留完整语义
2. 保留完整发音
3. 保留原始声线
4. 保留原始情绪
5. 保留自然节奏
6. 提升听感

当优化与自然度冲突：**永远优先自然度**。

## 开发阶段

- [x] Phase 1: 基础框架、文件上传、任务系统、日志系统
- [ ] Phase 2: ASR 引擎、时间轴、文本解析
- [ ] Phase 3: 内容分析、语气词、卡顿、停顿、重复句
- [ ] Phase 4: 编辑引擎、切割、重组、Crossfade
- [ ] Phase 5: DSP 处理链、全部后期模块
- [ ] Phase 6: 质量检查、自动回退、自动重处理
- [ ] Phase 7: Agent 模式、自动分析、自动决策、自动剪辑、自动导出

## 技术栈

- **后端**: Python 3.12 + FastAPI
- **前端**: Next.js
- **数据库**: SQLite
- **音频处理**: Faster Whisper, Librosa, Pydub, Pedalboard, WebRTCVAD, Pyloudnorm, Noisereduce
- **NLP**: Sentence-BERT

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
voiceflow-cn/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── analysis/
│   │   ├── editing/
│   │   ├── dsp/
│   │   ├── validator/
│   │   ├── plugins/
│   │   └── main.py
│   ├── tests/
│   ├── config.yaml
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   └── pages/
└── docs/
