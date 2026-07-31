// damage_vignette.gdshader — Red screen-edge vignette that flashes on player damage
// and fades out. Attach to a full-screen ColorRect node in the HUD layer.
shader_type canvas_item;

uniform vec4  vignette_color : source_color = vec4(0.7, 0.05, 0.05, 1.0);
uniform float vignette_radius : hint_range(0.3, 1.0) = 0.62;
uniform float vignette_softness : hint_range(0.1, 0.6) = 0.35;
// alpha_strength is driven by GDScript (set to 0.0 normally, spike on damage)
uniform float alpha_strength : hint_range(0.0, 1.0) = 0.0;

// Chromatic aberration on hit
uniform float aberration : hint_range(0.0, 0.02) = 0.0;
uniform sampler2D screen_texture : hint_screen_texture, repeat_disable, filter_linear_mipmap;

void fragment() {
    vec2 uv = SCREEN_UV;
    vec2 center = uv - vec2(0.5);
    float dist = length(center);
    float vig  = smoothstep(vignette_radius, vignette_radius - vignette_softness, dist);
    float edge_mask = 1.0 - vig;

    // Chromatic aberration when hit
    vec3 scene_r = texture(screen_texture, uv + vec2( aberration, 0.0)).rgb;
    vec3 scene_g = texture(screen_texture, uv).rgb;
    vec3 scene_b = texture(screen_texture, uv - vec2( aberration, 0.0)).rgb;
    vec3 scene   = vec3(scene_r.r, scene_g.g, scene_b.b);

    vec3 blended = mix(scene, vignette_color.rgb, edge_mask * alpha_strength);
    COLOR = vec4(blended, alpha_strength * edge_mask);
}
