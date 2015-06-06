#version 120

/*
 * Copyright 2010 Howard Hughes Medical Institute.
 * All rights reserved.
 * Use is subject to Janelia Farm Research Campus Software Copyright 1.1
 * license terms ( http://license.janelia.org/license/jfrc_copyright_1_1.html ).
 */

// CONES
// Methods for ray casting cone geometry from imposter geometry

// First phase of cone imposter shading: Compute linear coefficients in vertex shader,
// to ease burden on fragment shader
vec3 cone_linear_coeffs1(vec3 center, float radius, vec3 axis, float taper, vec3 pos) {
    // "A" parameter of quadratic formula is nonlinear, but has two linear components
    vec3 a = normalize(axis);
    float tAP = taper * dot(a, pos); // (2)
    // "C" parameter of quadratic formula is complicated, but is constant wrt position
    vec3 cCrossA = cross(center, a);
    float tAC = taper * dot(a, center);
    float qe_C = dot(cCrossA, cCrossA) - radius*radius ; // + (2*radius - tAC)*tAC; // (3) // TODO - restore non-cylinder component
    // "B" parameter
    vec3 qe_undot_b_part = vec3(
        dot(center, vec3(-a.y*a.y -a.z*a.z, a.x*a.y,          a.x*a.z)),
        dot(center, vec3( a.x*a.y,         -a.x*a.x -a.z*a.z, a.y*a.z)),
        dot(center, vec3( a.x*a.z,          a.y*a.z,          -a.x*a.x -a.y*a.y))
    );
    float qe_B = dot(pos, qe_undot_b_part); //  - tAP * (radius - tAC); // TODO - restore non-cylinder part

    return vec3(tAP, qe_C, qe_B);
}

// First phase of cone imposter shading: Compute linear coefficients in vertex shader,
// to ease burden on fragment shader
vec3 cone_linear_coeffs2(vec3 center, float radius, vec3 axis, float taper, vec3 pos) {
    // "A" parameter of quadratic formula is nonlinear, but has two linear components
    vec3 a = normalize(axis);
    return cross(pos, a); // (1)
}

// Second phase of sphere imposter shading: Compute nonlinear coefficients
// in fragment shader, including discriminant used to reject fragments.
vec2 cone_nonlinear_coeffs(vec3 pos, vec3 tap_qec_qeb, vec3 qe_undot_half_a) {
    // set up quadratic formula for sphere surface ray casting
    float half_b = tap_qec_qeb.z;
    float tAP = tap_qec_qeb.x;
    float a = dot(qe_undot_half_a, qe_undot_half_a); // - tAP * tAP; // TODO - restore non-cylinder component
    float c = tap_qec_qeb.y;
    float discriminant = (half_b*half_b - a*c);
    return vec2(a, discriminant);
}

// Third and final phase of sphere imposter shading: Compute sphere
// surface XYZ coordinates in fragment shader.
vec3 cone_surface_from_coeffs(vec3 pos, vec3 tap_qec_qeb, vec2 a2_d) {
    float discriminant = a2_d.y; // Negative values should be discarded.
    float a2 = a2_d.x;
    float b = tap_qec_qeb.z;
    float left = b / a2;
    float right = sqrt(discriminant) / a2;
    float alpha1 = left - right; // near surface of sphere
    // float alpha2 = left + right; // far/back surface of sphere
    return alpha1 * pos;
}


// SPHERES
// Methods for ray casting sphere geometry from imposter geometry


// First phase of sphere imposter shading: Compute linear coefficients in vertex shader,
// to ease burden on fragment shader
vec2 sphere_linear_coeffs(vec3 center, float radius, vec3 pos) {
    float pc = dot(pos, center);
    float c2 = dot(center, center) - radius * radius;
    return vec2(pc, c2);
}

// Second phase of sphere imposter shading: Compute nonlinear coefficients
// in fragment shader, including discriminant used to reject fragments.
vec2 sphere_nonlinear_coeffs(vec3 pos, vec2 pc_c2) {
    // set up quadratic formula for sphere surface ray casting
    float b = pc_c2.x;
    float a2 = dot(pos, pos);
    float c2 = pc_c2.y;
    float discriminant = b*b - a2*c2;
    return vec2(a2, discriminant);
}

// Third and final phase of sphere imposter shading: Compute sphere
// surface XYZ coordinates in fragment shader.
vec3 sphere_surface_from_coeffs(vec3 pos, vec2 pc_c2, vec2 a2_d) {
    float discriminant = a2_d.y; // Negative values should be discarded.
    float a2 = a2_d.x;
    float b = pc_c2.x;
    float left = b / a2;
    float right = sqrt(discriminant) / a2;
    float alpha1 = left - right; // near surface of sphere
    // float alpha2 = left + right; // far/back surface of sphere
    return alpha1 * pos;
}

// Hard coded light system, just for testing.
// Light parameters should be same ones in CPU host program, for comparison
vec3 light_rig(vec4 pos, vec3 normal, vec3 surface_color) {
    const vec3 ambient_light = vec3(0.2, 0.2, 0.2);
    const vec3 diffuse_light = vec3(0.8, 0.8, 0.8);
    const vec3 specular_light = vec3(0.8, 0.8, 0.8);
    const vec4 light_pos = vec4(-5, 3, 3, 0); 
    // const vec3 surface_color = vec3(1, 0.5, 1);

    vec3 surfaceToLight = normalize(light_pos.xyz); //  - (pos / pos.w).xyz);
    
    float diffuseCoefficient = max(0.0, dot(normal, surfaceToLight));
    vec3 diffuse = diffuseCoefficient * surface_color * diffuse_light;

    vec3 ambient = ambient_light * surface_color;
    
    vec3 surfaceToCamera = normalize(-pos.xyz); //also a unit vector    
    // Use Blinn-Phong specular model, to match fixed-function pipeline result (at least on nvidia)
    vec3 H = normalize(surfaceToLight + surfaceToCamera);
    float nDotH = max(0.0, dot(normal, H));
    float specularCoefficient = pow(nDotH, 100);
    vec3 specular = specularCoefficient * specular_light;

    return diffuse + specular + ambient;        
}

float fragDepthFromEyeXyz(vec3 eyeXyz) {
    // From http://stackoverflow.com/questions/10264949/glsl-gl-fragcoord-z-calculation-and-setting-gl-fragdepth
    // NOTE: change far and near to constant 1.0 and 0.0 might be worth trying for performance optimization
    float far=gl_DepthRange.far; // usually 1.0
    float near=gl_DepthRange.near; // usually 0.0

    vec4 eye_space_pos = vec4(eyeXyz, 1);
    vec4 clip_space_pos = gl_ProjectionMatrix * eye_space_pos;
    
    float ndc_depth = clip_space_pos.z / clip_space_pos.w;
    
    float depth = (((far-near) * ndc_depth) + near + far) / 2.0;
    return depth;
}
