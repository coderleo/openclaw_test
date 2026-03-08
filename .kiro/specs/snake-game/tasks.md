# 实现计划：贪吃蛇游戏

## 概述

基于 HTML5 Canvas 的贪吃蛇游戏，使用纯原生 HTML5、CSS3 和 JavaScript 实现。所有文件存放在 `snake-game/` 文件夹中，浏览器直接打开 `index.html` 即可运行。采用增量开发方式，先搭建核心骨架，再逐步实现各模块功能，最后整合视觉效果。

## 任务

- [x] 1. 搭建项目结构与核心框架
  - [x] 1.1 创建项目文件结构和入口页面
    - 创建 `snake-game/` 文件夹
    - 创建 `snake-game/index.html`：包含 Canvas 元素（600x600）、UI 容器（开始按钮、重新开始按钮）、引入 style.css 和 game.js
    - 创建 `snake-game/style.css`：页面布局、Canvas 居中、按钮样式、覆盖层样式
    - 创建 `snake-game/game.js`：定义常量（CANVAS_SIZE=600, CELL_SIZE=20, GRID_SIZE=30）、等级主题配色数组 LEVEL_THEMES
    - _需求: 9.1, 9.2, 9.3_

  - [x] 1.2 实现 GameEngine 类骨架与状态管理
    - 实现 GameEngine 构造函数：初始化 canvas、ctx、state='menu'、score=0、level=1
    - 实现 init()：设置高清适配、显示主菜单、绑定按钮事件
    - 实现 start()：初始化蛇、食物、重置分数和等级，切换 state='playing'
    - 实现 togglePause()：在 'playing' 和 'paused' 之间切换
    - 实现 gameOver()：设置 state='gameover'、保存最高分
    - 实现 restart()：调用 start() 重新开始
    - 实现 saveHighScore() / loadHighScore()：localStorage 读写，含 try-catch 错误处理
    - _需求: 1.1, 1.3, 4.3, 4.4, 6.3, 6.4, 7.1_

- [x] 2. 实现蛇的核心逻辑
  - [x] 2.1 实现 Snake 类
    - 实现构造函数：初始化 body 数组（起始位置在网格中央）、direction='right'、nextDirection='right'
    - 实现 move()：在头部插入新坐标，移除尾部（普通移动）
    - 实现 grow()：标记下次移动不移除尾部
    - 实现 setDirection(dir)：含防掉头校验（上↔下、左↔右互斥）
    - 实现 getHead()：返回 body[0]
    - 实现 containsPoint(x, y)：遍历 body 判断坐标是否在蛇身上
    - _需求: 2.1, 2.2, 2.3, 3.2_

  - [x] 2.2 编写 Snake 属性测试：防掉头
    - **Property 2: 方向键防掉头**
    - 使用 fast-check 生成随机 (当前方向, 新方向) 对，验证 180° 反向时方向不变，否则更新
    - **验证: 需求 2.1, 2.2**

  - [x] 2.3 编写 Snake 属性测试：每帧移动一格
    - **Property 3: 蛇每帧移动一格**
    - 使用 fast-check 生成随机方向和有效网格坐标，验证移动后头部恰好偏移一个网格单元
    - **验证: 需求 2.3**

  - [x] 2.4 编写 Snake 属性测试：吃食物蛇身增长
    - **Property 7: 吃食物蛇身增长**
    - 使用 fast-check 生成随机长度的蛇，验证吃食物后长度 N → N+1
    - **验证: 需求 3.2**

- [x] 3. 实现输入处理与碰撞检测
  - [x] 3.1 实现 InputHandler 类
    - 实现构造函数：绑定 keydown 事件监听
    - 实现 handleKeyDown(event)：处理方向键和空格键，忽略其他按键
    - 实现输入节流：每个移动间隔只接受第一次有效方向输入（lock/unlock 机制）
    - 实现 getNextDirection()：获取并消费待处理方向
    - _需求: 2.1, 2.5, 7.1_

  - [x] 3.2 编写 InputHandler 属性测试：输入节流
    - **Property 5: 输入节流**
    - 使用 fast-check 生成随机方向输入序列（2~10个），验证仅第一次有效输入被采纳
    - **验证: 需求 2.5**

  - [x] 3.3 实现 CollisionDetector 类
    - 实现 checkSelfCollision(snake)：蛇头是否与自身非头部段重合
    - 实现 checkBoundaryCollision(head, gridW, gridH)：蛇头是否超出 [0, gridSize-1] 范围
    - 实现 checkObstacleCollision(head, obstacles)：蛇头是否与任意障碍物重合
    - 实现 checkFoodCollision(head, food)：蛇头是否与食物重合
    - _需求: 4.1, 4.2, 2.4, 3.2_

  - [x] 3.4 编写 CollisionDetector 属性测试：边界碰撞
    - **Property 4: 边界碰撞检测**
    - 使用 fast-check 生成边缘坐标和朝外方向，验证碰撞检测判定为越界
    - **验证: 需求 2.4**

  - [x] 3.5 编写 CollisionDetector 属性测试：自身碰撞
    - **Property 9: 自身碰撞检测**
    - 使用 fast-check 生成随机蛇身体（含/不含自交叉），验证碰撞检测正确性
    - **验证: 需求 4.1**

  - [x] 3.6 编写 CollisionDetector 属性测试：障碍物碰撞
    - **Property 10: 障碍物碰撞检测**
    - 使用 fast-check 生成随机蛇头坐标和障碍物集合，验证碰撞检测正确性
    - **验证: 需求 4.2**

- [x] 4. 检查点 - 核心逻辑验证
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 5. 实现食物生成与关卡系统
  - [x] 5.1 实现 Food 类
    - 实现构造函数：初始化 position
    - 实现 spawn(gridWidth, gridHeight, occupiedCells)：在空闲位置随机生成食物
    - 处理网格已满的情况：遍历所有格子查找空位，无空位则返回 null（触发通关）
    - _需求: 3.1, 3.4, 3.5_

  - [x] 5.2 编写 Food 属性测试：食物生成不重叠
    - **Property 6: 食物生成不重叠**
    - 使用 fast-check 生成随机蛇身体和障碍物集合，验证食物坐标不与已占用位置重合
    - **验证: 需求 3.1, 3.4**

  - [x] 5.3 实现 LevelSystem 类
    - 实现 getThreshold(level)：返回 level × 50
    - 实现 getScorePerFood(level)：返回 level × 10
    - 实现 getMoveInterval(level)：返回 Math.floor(200 × 0.9^(level-1))
    - 实现 getObstacleCount(level)：level < 3 返回 0，否则返回 level
    - 实现 checkLevelUp(score, currentLevel)：判断是否升级
    - 支持至少 10 个等级
    - _需求: 5.1, 5.2, 5.3, 5.6_

  - [x] 5.4 编写 LevelSystem 属性测试：升级阈值
    - **Property 11: 等级升级阈值**
    - 使用 fast-check 生成随机等级和分数，验证 S ≥ L×50 时触发升级
    - **验证: 需求 5.1**

  - [x] 5.5 编写 LevelSystem 属性测试：移动速度公式
    - **Property 12: 移动速度公式**
    - 使用 fast-check 生成随机等级 (1-10)，验证移动间隔等于 200 × 0.9^(L-1)
    - **验证: 需求 5.2**

  - [x] 5.6 编写 LevelSystem 属性测试：障碍物数量
    - **Property 13: 障碍物数量与等级关系**
    - 使用 fast-check 生成随机等级 (1-10)，验证 L<3 时为 0，L≥3 时为 L
    - **验证: 需求 5.3**

  - [x] 5.7 编写分数属性测试：吃食物分数计算
    - **Property 8: 吃食物分数计算**
    - 使用 fast-check 生成随机等级和分数，验证吃食物后分数 S → S + L×10
    - **验证: 需求 3.3**

- [x] 6. 实现分数管理与暂停功能
  - [x] 6.1 实现 ScoreBoard 分数逻辑
    - 在 GameEngine 中实现分数累加逻辑：吃食物时 score += level × 10
    - 实现最高分实时更新：当 score > highScore 时更新 highScore
    - 实现 localStorage 持久化：saveHighScore / loadHighScore，含错误处理（try-catch、NaN 校验）
    - _需求: 3.3, 6.1, 6.2, 6.3, 6.4_

  - [x] 6.2 编写分数属性测试：最高分实时更新
    - **Property 15: 最高分实时更新**
    - 使用 fast-check 生成随机 (当前最高分, 新分数) 对，验证更新逻辑
    - **验证: 需求 6.2**

  - [x] 6.3 编写分数属性测试：最高分持久化往返
    - **Property 14: 最高分持久化往返**
    - 使用 fast-check 生成随机非负整数，验证 localStorage 存取一致性
    - **验证: 需求 6.3, 6.4**

  - [x] 6.4 完善暂停功能与状态管理
    - 确保暂停时游戏循环不更新蛇的位置
    - 确保暂停时不响应方向键输入
    - 确保只有 'playing' 状态才能暂停
    - _需求: 7.1, 7.2, 7.3_

  - [x] 6.5 编写暂停属性测试：暂停切换往返
    - **Property 16: 暂停切换往返**
    - 验证 playing → paused → playing 状态转换正确性
    - **验证: 需求 7.1**

  - [x] 6.6 编写暂停属性测试：暂停时蛇不移动
    - **Property 17: 暂停时蛇不移动**
    - 使用 fast-check 生成随机蛇身体配置，验证暂停状态下更新后蛇身不变
    - **验证: 需求 7.3**

- [x] 7. 检查点 - 游戏逻辑完整性验证
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 8. 实现渲染器与视觉效果
  - [x] 8.1 实现 Renderer 类基础渲染
    - 实现 setupHiDPI()：根据 devicePixelRatio 设置 Canvas 内部尺寸和 CSS 尺寸
    - 实现 clear()：清空画布
    - 实现 drawGrid(level)：绘制网格背景，使用等级对应的主题配色
    - 实现 drawSnake(snake, direction)：渐变色蛇身 + 头部眼睛（朝向与方向一致）+ 圆角 + 阴影
    - 实现 drawFood(food)：带光泽高光效果的食物图形
    - 实现 drawObstacles(obstacles)：绘制障碍物
    - _需求: 1.2, 1.4, 1.5, 8.1, 8.2, 8.3, 8.6_

  - [x] 8.2 编写 Renderer 属性测试：HiDPI 缩放正确性
    - **Property 1: HiDPI 缩放正确性**
    - 使用 fast-check 生成随机正数 dpr (0.5~4.0)，验证 Canvas 内部尺寸 = 逻辑尺寸 × dpr
    - **验证: 需求 1.2**

  - [x] 8.3 编写等级主题属性测试：等级主题映射
    - **Property 18: 等级主题映射**
    - 使用 fast-check 生成随机等级 (1-10)，验证主题配色与 LEVEL_THEMES[L-1] 一致
    - **验证: 需求 8.6**

  - [x] 8.4 实现 UI 渲染方法
    - 实现 drawScoreBoard(score, level, highScore)：画布顶部显示分数面板
    - 实现 drawMenu()：主菜单界面（含"开始游戏"按钮）
    - 实现 drawGameOver(score, level)：游戏结束画面（含最终分数、等级、"重新开始"按钮）
    - 实现 drawVictory(score)：通关画面
    - 实现 drawPauseOverlay()：暂停遮罩（"已暂停"提示文字）
    - _需求: 1.3, 4.3, 4.4, 6.1, 7.2_

  - [x] 8.5 实现 ParticleSystem 与动画效果
    - 实现 ParticleSystem 类：emit()、update()、draw()
    - 实现吃食物时的粒子扩散动画
    - 实现 drawLevelUpAnimation()：等级提升过渡动画（≤1.5秒）
    - 实现平滑帧动画渲染（requestAnimationFrame，≥30 FPS）
    - _需求: 8.4, 8.5, 5.4_

- [x] 9. 整合游戏循环与完整流程
  - [x] 9.1 实现完整游戏循环
    - 实现 gameLoop(timestamp)：使用 requestAnimationFrame 驱动
    - 在每帧中按顺序执行：获取输入 → 更新蛇 → 碰撞检测 → 食物判定 → 等级检查 → 渲染
    - 实现基于移动间隔的逻辑更新节奏（根据等级调整间隔）
    - 整合所有组件：Snake、Food、LevelSystem、CollisionDetector、InputHandler、Renderer、ParticleSystem
    - _需求: 2.3, 3.2, 3.3, 3.4, 4.1, 4.2, 5.1, 5.2, 5.3_

  - [x] 9.2 实现等级升级完整流程
    - 升级时：提升等级、加快速度、生成障碍物（≥3级）、播放升级动画、更新分数面板
    - 障碍物生成不与蛇和食物重叠
    - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 9.3 实现游戏结束与重新开始完整流程
    - 游戏结束：暂停循环、显示结束画面（分数+等级）、保存最高分、显示重新开始按钮
    - 通关：显示胜利画面
    - 重新开始：重置所有状态，从第一关开始
    - _需求: 3.5, 4.3, 4.4, 6.3_

- [x] 10. 最终检查点 - 全面验证
  - 确保所有测试通过，如有问题请向用户确认。

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加快 MVP 开发
- 每个任务引用了对应的需求编号，确保可追溯性
- 检查点任务用于增量验证，确保每个阶段的正确性
- 属性测试使用 fast-check 库，验证通用正确性属性
- 单元测试验证具体示例和边界情况
- 所有代码使用原生 JavaScript，无外部框架依赖
