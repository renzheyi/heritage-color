"""演示：三个功能的完整调用。运行：python -m heritage_color.demo"""

import json
from heritage_color import auth_color, infer_pigment, decide_restoration


def show(title, obj):
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(json.dumps(obj.to_dict() if hasattr(obj, "to_dict") else obj,
                     ensure_ascii=False, indent=2))
    print()


def main():
    # 1) 色彩考证：现存色发暗的红色柱子，清代，文献记载"朱柱青檐"
    r1 = auth_color(observed_hex="#6E2020", dynasty="清",
                    document_text="檐下青绿彩画，朱柱，间以金线")
    show("① 色彩考证", r1)

    # 2) 颜料推演：推断出的青绿色可能用什么颜料
    r2 = infer_pigment(r1.original_hex, dynasty="清")
    show("② 颜料推演", r2)

    # 3) 修复决策：铅白变黑 + 环境湿度过高
    r3 = decide_restoration(pigment="铅白", damage="变黑",
                            environment={"湿度": "75% RH"})
    show("③ 修复决策", r3)


if __name__ == "__main__":
    main()
