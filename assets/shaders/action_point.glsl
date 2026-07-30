// rotating_squares.glsl

// 定义一个绘制矩形框的函数，center: 中心点, size: 半边长, color: 颜色
vec4 drawSquareFrame(vec2 uv, vec2 center, float size, vec4 color) {
    vec2 delta = uv - center;
    vec2 distToEdge = max(abs(delta) - size, 0.0);
    float dist = length(distToEdge);
    float borderWidth = 0.1;
    float glow = pow(1.0 - smoothstep(0.0, borderWidth, dist), 0.5);
    // 颜色随 glow 衰减
    return vec4(color.rgb * glow, glow * color.a);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // 1. 坐标归一化：将像素坐标转换为 0~1 的范围，方便在不同分辨率下工作[reference:3]
    vec2 uv = fragCoord / iResolution.xy;

    // 2. 修正宽高比：确保正方形在屏幕上看起来是正的，而非被拉伸
    float aspect = iResolution.x / iResolution.y;
    vec2 uvCorrected = uv - 0.5;          // 将原点移动到屏幕中心
    uvCorrected.x *= aspect;              // 修正宽高比

    // 3. 绘制两个嵌套的正方形框
    // 外框：颜色为青色 (0, 1, 1)，半边长 0.3
    vec4 outerColor = vec4(0.0, 1.0, 1.0, 1.0);
    // 内框：颜色为品红 (1, 0, 1)，半边长 0.2
    vec4 innerColor = vec4(1.0, 0.0, 1.0, 1.0);

    // 4. 让两个正方形绕中心旋转，速度不同
    float angleOuter = iTime * 0.5;        // 外框旋转速度
    float angleInner = -iTime * 0.8;       // 内框反向旋转，速度更快

    // 构建旋转矩阵
    float cosA = cos(angleOuter);
    float sinA = sin(angleOuter);
    // 应用旋转矩阵到归一化坐标上
    vec2 rotatedUvOuter = vec2(uvCorrected.x * cosA - uvCorrected.y * sinA,
                               uvCorrected.x * sinA + uvCorrected.y * cosA);

    cosA = cos(angleInner);
    sinA = sin(angleInner);
    vec2 rotatedUvInner = vec2(uvCorrected.x * cosA - uvCorrected.y * sinA,
                               uvCorrected.x * sinA + uvCorrected.y * cosA);

    // 5. 分别获取两个框的发光颜色（每个像素的透明度代表发光强度）
    vec4 outerGlow = drawSquareFrame(rotatedUvOuter, vec2(0.0), 0.3, outerColor);
    vec4 innerGlow = drawSquareFrame(rotatedUvInner, vec2(0.0), 0.2, innerColor);
    // screen 混合，现在透明区域 RGB 为 0，不会产生白色
    vec3 finalColor = 1.0 - (1.0 - outerGlow.rgb) * (1.0 - innerGlow.rgb);
    float finalAlpha = max(outerGlow.a, innerGlow.a);
    fragColor = vec4(finalColor, finalAlpha);
}