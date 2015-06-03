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

// Final non-linear computation, to be performed in fragment shader
vec3 sphere_surface_from_coeffs(vec3 pos, vec2 pc_c2) {
    // set up quadratic formula for sphere surface ray casting
    float b = pc_c2.x;
    float a2 = dot(pos, pos);
    float c2 = pc_c2.y;
    float discriminant = b*b - a2*c2;
    if (discriminant <= 0)
        discard; // Point does not intersect sphere
    float left = b / a2;
    float right = sqrt(discriminant) / a2;
    float alpha1 = left - right; // near surface of sphere
    // float alpha2 = left + right; // far/back surface of sphere
    return alpha1 * pos;
}

// Pedagogical method, which does full ray casting of sphere imposter.
// In practice, this method is divided into vertex and fragment components
// center: center of sphere in camera frame
// pos: location of imposter geometry in camera frame
vec3 sphere_surface_from_imposter_pos(vec3 center, float radius, vec3 pos) {
    vec2 pc_c2 = sphere_linear_coeffs(center, radius, pos); // should run in vertex shader
    vec3 s = sphere_surface_from_coeffs(pos, pc_c2); // should run in fragment shader
    // vec3 normal = 1.0/radius * (s - center);
    return s;
}

/* simple function for debugging */
void set_green_color() { 
    gl_FragColor = vec4( 0, 1, 0, 1 ); 
}
