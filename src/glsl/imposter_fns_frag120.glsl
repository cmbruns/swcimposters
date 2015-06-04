#version 120

/*
 * Copyright 2010 Howard Hughes Medical Institute.
 * All rights reserved.
 * Use is subject to Janelia Farm Research Campus Software Copyright 1.1
 * license terms ( http://license.janelia.org/license/jfrc_copyright_1_1.html ).
 */

// SPHERES
// Methods for ray casting sphere geometry from imposter geometry

// defined in imposter_fns.glsl
vec2 sphere_linear_coeffs(vec3 center, float radius, vec3 pos);
vec2 sphere_nonlinear_coeffs(vec3 pos, vec2 pc_c2);
vec3 sphere_surface_from_coeffs(vec3 pos, vec2 pc_c2, vec2 a2_d);

// Pedagogical method, which does full ray casting of sphere imposter.
// In practice, this method is divided into vertex and fragment components
// center: center of sphere in camera frame
// pos: location of imposter geometry in camera frame
vec3 sphere_surface_from_imposter_pos(vec3 center, float radius, vec3 pos) {
    vec2 pc_c2 = sphere_linear_coeffs(center, radius, pos); // should run in vertex shader
    vec2 a2_d = sphere_nonlinear_coeffs(pos, pc_c2); // should run in fragment shader
    if (a2_d.y <= 0)
        discard; // Point does not intersect sphere
    return sphere_surface_from_coeffs(pos, pc_c2, a2_d);
}

/* simple function for debugging */
void set_green_color() { 
    gl_FragColor = vec4( 0, 1, 0, 1 ); 
}
