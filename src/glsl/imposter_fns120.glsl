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
    // TODO Copying from cinemol until debugged
    vec3 p1 = center + axis;
    vec3 p2 = center - axis;
    vec3 middle = center;
    vec3 bondVec = p2 - p1; // -2 * axis?
    float bondLengthSqr = dot(bondVec, bondVec);
    float maxCDistSqr = 1.00 * (0.25 * bondLengthSqr * radius * radius); // TODO - not so for cone
    vec3 cylCen = 0.5 * (p1 + p2); // center?
    vec3 cylAxis = normalize(-axis);
    
    // "A" parameter of quadratic formula is nonlinear, but has two linear components
    // vec3 a = normalize(axis);
    
    // "B" parameter
    float tAP = taper * dot(cylAxis, pos); // (2)
    float tAC = taper * dot(cylAxis, cylCen);
    vec3 x = cylAxis;
    vec3 qe_undot_b_part = vec3(
        dot(cylCen, vec3(-x.y*x.y -x.z*x.z, x.x*x.y, x.x*x.z)),
        dot(cylCen, vec3( x.x*x.y, -x.x*x.x - x.z*x.z, x.y*x.z)),
        dot(cylCen, vec3( x.x*x.z,  x.y*x.z, -x.x*x.x - x.y*x.y)));
    float qe_half_b = dot(pos, qe_undot_b_part) - tAP * (radius - tAC);
    
    // "C" parameter of quadratic formula is complicated, but is constant wrt position
    vec3 cxa = cross(cylCen, cylAxis);
    float qe_c = dot(cxa, cxa) - radius * radius + (2*radius - tAC)*tAC;
    // float qe_C = dot(cxa, cxa) - radius*radius ; // + (2*radius - tAC)*tAC; // (3) // TODO - restore non-cylinder component

    return vec3(tAP, qe_c, qe_half_b);
}

// First phase of cone imposter shading: Compute linear coefficients in vertex shader,
// to ease burden on fragment shader
void cone_linear_coeffs2(vec3 center, float radius, vec3 axis, float taper, vec3 pos,
        out vec3 qe_undot_half_a) 
{
    // "A" parameter of quadratic formula is nonlinear, but has two linear components
    vec3 cylAxis = normalize(-axis);
    qe_undot_half_a = cross(pos, cylAxis); // (1)
}

// Second phase of sphere imposter shading: Compute nonlinear coefficients
// in fragment shader, including discriminant used to reject fragments.
void cone_nonlinear_coeffs(vec3 pos, vec3 tap_qec_qeb, vec3 qe_undot_half_a,
    out float qe_half_a, out float discriminant) 
{
    // set up quadratic formula for sphere surface ray casting
    float qe_half_b = tap_qec_qeb.z;
    float tAP = tap_qec_qeb.x;
    qe_half_a = dot(qe_undot_half_a, qe_undot_half_a) - tAP * tAP; // TODO - restore non-cylinder component
    float qe_c = tap_qec_qeb.y;
    discriminant = qe_half_b * qe_half_b - qe_half_a * qe_c;
}

// Third and final phase of sphere imposter shading: Compute sphere
// surface XYZ coordinates in fragment shader.
void cone_surface_from_coeffs(in vec3 pos, in vec3 tap_qec_qeb, in float qe_half_a, in float discriminant, 
    out vec3 surface_pos)
{
    float qe_half_b = tap_qec_qeb.z;
    float left = -qe_half_b / qe_half_a;
    float right = sqrt(discriminant) / qe_half_a;
    float alpha1 = left - right; // near surface of sphere
    // float alpha2 = left + right; // far/back surface of sphere
    surface_pos = alpha1 * pos;
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
