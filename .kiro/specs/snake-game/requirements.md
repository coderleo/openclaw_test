# 需求文档

## 简介

贪吃蛇游戏是一款基于 HTML5 Canvas 的经典街机游戏。玩家控制一条蛇在画布上移动，吃掉食物后蛇身变长、得分增加。游戏包含关卡升级系统，随着等级提升，蛇的移动速度加快并出现障碍物，画面采用高清渲染以呈现逼真的视觉效果。整个游戏打包在一个独立文件夹中，可直接在浏览器中运行。

## 术语表

- **Game_Engine**: 贪吃蛇游戏的核心运行引擎，负责游戏循环、状态管理和渲染
- **Snake**: 玩家控制的蛇对象，由一系列连续的身体段组成
- **Food**: 随机出现在画布上的食物对象，蛇吃掉后获得分数
- **Canvas**: HTML5 Canvas 画布元素，用于渲染游戏画面
- **Level_System**: 关卡升级系统，根据玩家得分决定当前等级和难度
- **Obstacle**: 障碍物对象，在高等级关卡中出现，蛇碰到后游戏结束
- **Score_Board**: 分数显示面板，展示当前分数、等级和最高分
- **Renderer**: 高清渲染器，负责将游戏元素以高质量画面绘制到 Canvas 上

## 需求

### 需求 1：游戏初始化与画布渲染

**用户故事：** 作为玩家，我希望打开游戏后看到一个清晰、美观的游戏界面，以便获得良好的视觉体验。

#### 验收标准

1. WHEN 玩家打开游戏页面, THE Game_Engine SHALL 创建一个尺寸不小于 600x600 像素的 Canvas 画布
2. THE Renderer SHALL 根据设备像素比（devicePixelRatio）对 Canvas 进行高清适配，确保在高分辨率屏幕上画面清晰无模糊
3. WHEN 游戏加载完成, THE Game_Engine SHALL 显示包含"开始游戏"按钮的主菜单界面
4. THE Renderer SHALL 使用渐变色、阴影和圆角等视觉效果渲染蛇身，使蛇的外观具有立体感
5. THE Renderer SHALL 为 Food 绘制带有光泽高光效果的图形，使食物外观逼真

### 需求 2：蛇的移动与控制

**用户故事：** 作为玩家，我希望通过键盘方向键控制蛇的移动方向，以便在游戏中灵活操作。

#### 验收标准

1. WHEN 玩家按下方向键（上、下、左、右）, THE Game_Engine SHALL 将 Snake 的移动方向更改为对应方向
2. THE Game_Engine SHALL 阻止 Snake 直接掉头（即从当前方向反转 180 度）
3. WHILE 游戏处于运行状态, THE Snake SHALL 按照当前方向以固定时间间隔自动向前移动一格
4. WHEN Snake 移动超出 Canvas 边界, THE Game_Engine SHALL 判定游戏结束
5. WHEN 玩家在移动间隔内多次按下方向键, THE Game_Engine SHALL 仅响应第一次有效的方向变更输入

### 需求 3：食物生成与吃食逻辑

**用户故事：** 作为玩家，我希望蛇吃到食物后身体变长并获得分数，以便感受游戏的成长乐趣。

#### 验收标准

1. WHEN 游戏开始, THE Game_Engine SHALL 在 Canvas 上随机生成一个 Food，且 Food 的位置不与 Snake 身体重叠
2. WHEN Snake 的头部坐标与 Food 的坐标重合, THE Game_Engine SHALL 将 Snake 的长度增加一个身体段
3. WHEN Snake 吃掉 Food, THE Score_Board SHALL 将当前分数增加该等级对应的分值（等级 × 10 分）
4. WHEN Snake 吃掉 Food, THE Game_Engine SHALL 立即在新的随机位置生成一个新的 Food，且新位置不与 Snake 身体或 Obstacle 重叠
5. IF Canvas 上没有可用的空位生成 Food, THEN THE Game_Engine SHALL 判定玩家通关并显示胜利画面

### 需求 4：碰撞检测

**用户故事：** 作为玩家，我希望游戏能准确检测碰撞，以便游戏规则公平可靠。

#### 验收标准

1. WHEN Snake 的头部坐标与 Snake 自身任意身体段坐标重合, THE Game_Engine SHALL 判定游戏结束
2. WHEN Snake 的头部坐标与任意 Obstacle 的坐标重合, THE Game_Engine SHALL 判定游戏结束
3. WHEN 游戏结束, THE Game_Engine SHALL 暂停游戏循环并显示"游戏结束"画面，包含最终分数和当前等级
4. WHEN 游戏结束画面显示后, THE Game_Engine SHALL 提供"重新开始"按钮，允许玩家从第一关重新开始

### 需求 5：关卡升级系统

**用户故事：** 作为玩家，我希望游戏有关卡升级机制，以便随着游戏进展获得更大的挑战。

#### 验收标准

1. WHEN 玩家的累计分数达到当前等级的升级阈值（等级 × 50 分）, THE Level_System SHALL 将等级提升一级
2. WHEN 等级提升, THE Game_Engine SHALL 将 Snake 的移动速度提高 10%（缩短移动时间间隔）
3. WHEN 等级提升到 3 级及以上, THE Game_Engine SHALL 在 Canvas 上随机放置与当前等级数量相等的 Obstacle，且 Obstacle 不与 Snake 和 Food 重叠
4. WHEN 等级提升, THE Renderer SHALL 播放等级提升的视觉过渡动画（持续时间不超过 1.5 秒）
5. WHEN 等级提升, THE Score_Board SHALL 更新显示的当前等级数值
6. THE Level_System SHALL 支持至少 10 个等级

### 需求 6：分数与状态显示

**用户故事：** 作为玩家，我希望随时看到当前分数、等级和最高分，以便了解游戏进度。

#### 验收标准

1. WHILE 游戏处于运行状态, THE Score_Board SHALL 在画布顶部持续显示当前分数、当前等级和历史最高分
2. WHEN 当前分数超过历史最高分, THE Score_Board SHALL 实时更新历史最高分的显示值
3. WHEN 游戏结束, THE Game_Engine SHALL 将最高分保存到浏览器的 localStorage 中
4. WHEN 游戏加载, THE Game_Engine SHALL 从 localStorage 中读取并恢复历史最高分

### 需求 7：游戏暂停与恢复

**用户故事：** 作为玩家，我希望能暂停和恢复游戏，以便在需要时中断游戏。

#### 验收标准

1. WHEN 玩家按下空格键, THE Game_Engine SHALL 在运行状态和暂停状态之间切换
2. WHILE 游戏处于暂停状态, THE Renderer SHALL 在画布中央显示"已暂停"提示文字
3. WHILE 游戏处于暂停状态, THE Game_Engine SHALL 停止 Snake 的移动和游戏循环计时

### 需求 8：视觉效果与画面质量

**用户故事：** 作为玩家，我希望游戏画面精美逼真，以便获得沉浸式的游戏体验。

#### 验收标准

1. THE Renderer SHALL 为游戏背景绘制网格纹理，网格线使用半透明颜色以增加层次感
2. THE Renderer SHALL 为 Snake 的每个身体段使用从头到尾的渐变色，使蛇身呈现自然的色彩过渡
3. THE Renderer SHALL 为 Snake 的头部绘制眼睛图案，眼睛朝向与当前移动方向一致
4. THE Renderer SHALL 使用平滑的帧动画渲染 Snake 的移动过程，帧率不低于 30 FPS
5. WHEN Snake 吃掉 Food, THE Renderer SHALL 在 Food 位置播放粒子扩散动画效果
6. THE Renderer SHALL 根据当前等级切换不同的背景配色方案，每个等级具有独特的视觉主题

### 需求 9：项目结构与独立部署

**用户故事：** 作为开发者，我希望游戏代码组织在独立文件夹中，以便方便管理和部署。

#### 验收标准

1. THE Game_Engine SHALL 将所有游戏文件（HTML、CSS、JavaScript）存放在名为 `snake-game` 的独立文件夹中
2. THE Game_Engine SHALL 仅使用原生 HTML5、CSS3 和 JavaScript 实现，不依赖任何外部框架或库
3. WHEN 用户在浏览器中打开 `snake-game/index.html` 文件, THE Game_Engine SHALL 正常启动并运行游戏
