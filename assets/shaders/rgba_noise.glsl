void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
	vec2 uv = fragCoord.xy;
    
    uv -= floor(uv / 289.0) * 289.0;
    uv += vec2(223.35734, 550.56781);
    uv *= uv;
    
    float xy = uv.x * uv.y;
    
    fragColor = vec4(fract(xy * 0.00000012),
                     fract(xy * 0.00000543),
                     fract(xy * 0.00000192),
                     fract(xy * 0.00000423));
}