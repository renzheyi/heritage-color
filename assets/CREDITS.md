# 古建筑配图来源

本目录图片用于「文物色彩考证与修复辅助系统」网页装饰，均来自 **Pexels** 免费图库，按 [Pexels License](https://www.pexels.com/license/) 使用（可免费用于商业及非商业用途，无需署名；此处仍标注来源以表谢意）。

| 文件 | 主题 | 来源页面 | 授权 |
|---|---|---|---|
| `forbidden_city.jpg` | 北京故宫太和殿与汉白玉三台 | https://www.pexels.com/photo/18549556/ | Pexels License |
| `dunhuang.jpg` | 敦煌莫高窟崖壁石窟 | https://www.pexels.com/photo/25974825/ | Pexels License |
| `summer_palace.jpg` | 中式建筑琉璃脊饰与回纹彩画 | https://www.pexels.com/photo/29606793/ | Pexels License |
| `foguang_temple.jpg` | 传统彩画木雕与贴金造像 | https://www.pexels.com/photo/32762553/ | Pexels License |
| `potala.jpg` | 西藏布达拉宫 | https://www.pexels.com/photo/30136198/ | Pexels License |
| `arch_web.jpg` | 故宫太和殿正立面（描边背景原图） | https://www.pexels.com/photo/3229784/ | Pexels License |

图片经等比缩放（宽 1400px）后打包进项目，随代码部署到 Streamlit Cloud。

## 背景合成图

`bg_arch.jpg` 由 `arch_web.jpg`（上表第 6 张，网络检索的故宫太和殿照片）加工而成：
Sobel 边缘检测提取建筑主体描边 → 淡化天空地面 → 高斯虚化 → 叠加半透明方框万字回纹花纹 → 宣纸暖色底。
仅作页面淡淡衬底，不喧宾夺主。

## 古风小图标

`assets/emoji/*.png` 为网页与五个模块中插入的古风小图像（调色板 / 毛笔 / 古建筑 / 卷轴 / 石头 / 灯笼 / 龙 / 仙鹤 / 宝石等），
取自 **Twemoji**（Twitter 开源表情图，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)），通过 jsdelivr 镜像下载，
经 sepia 滤镜调和为古风色调后随代码打包部署。`montage.png` 仅为本地预览图，不参与运行。
