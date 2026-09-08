#ifdef GL_ES
precision mediump float;
#endif

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    vec4 orange = vec4(1.0, 0.5, 0.0, 1.0);
    fragColor = orange;
}