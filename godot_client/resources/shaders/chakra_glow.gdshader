// chakra_glow.gdshader — Glowing chakra energy shader for jutsu charge / UI bars.
// Use as an overlay on the chakra bar or on character mesh during charge.
shader_type canvas_item;

uniform vec4  glow_color  : source_color = vec4(0.3, 0.7, 1.0, 1.0);
uniform float pulse_speed : hint_range(0.5, 8.0) = 2.5;
uniform float glow_strength : hint_range(0.0, 3.0) = 1.4;
uniform float fill_ratio  : hint_range(0.0, 1.0)  = 1.0;  // set from GDScript
uniform sampler2D screen_texture : hint_screen_texture, repeat_disable, filter_linear_mipmap;

void fragment() {
    vec4 base = texture(TEXTURE, UV);

    // Horizontal fill (for HP/Chakra bars)
    float mask = step(UV.x, fill_ratio);

    // Pulse
    float pulse = 0.5 + 0.5 * sin(TIME * pulse_speed);
    float brightness = 1.0 + glow_strength * pulse;

    vec3 colored = glow_color.rgb * brightness;
    COLOR = vec4(colored * mask, base.a * mask + base.a * (1.0 - mask) * 0.25);
}
