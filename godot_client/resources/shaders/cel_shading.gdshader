// cel_shading.gdshader — Anime cel-shading surface shader.
// Apply to character materials for a stylized flat-shading + hard shadow look.
shader_type spatial;
render_mode diffuse_toon, specular_toon;

uniform vec4  albedo_color  : source_color = vec4(0.8, 0.7, 0.6, 1.0);
uniform sampler2D albedo_texture : source_color, hint_default_white;
uniform float cel_steps     : hint_range(1.0, 6.0, 1.0) = 3.0;
uniform vec4  outline_color : source_color = vec4(0.05, 0.05, 0.05, 1.0);
uniform float outline_width : hint_range(0.0, 0.02) = 0.006;
uniform float rim_power     : hint_range(0.5, 8.0) = 3.0;
uniform vec4  rim_color     : source_color = vec4(0.5, 0.8, 1.0, 1.0);

// Affinity tint (set from GDScript by material.set_shader_parameter)
uniform vec4  affinity_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float affinity_tint_strength : hint_range(0.0, 1.0) = 0.0;

void fragment() {
    vec4 tex = texture(albedo_texture, UV);
    vec3 base = mix(albedo_color.rgb, affinity_tint.rgb, affinity_tint_strength);
    base *= tex.rgb;
    ALBEDO = base;
    ALPHA  = tex.a * albedo_color.a;

    // Rim light
    float rim = 1.0 - dot(NORMAL, VIEW);
    rim = pow(rim, rim_power);
    EMISSION = rim_color.rgb * rim * 0.4;

    // Roughness / metallic
    ROUGHNESS = 0.85;
    METALLIC  = 0.0;
}
