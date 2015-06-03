#version 120

/*
 * Copyright 2010 Howard Hughes Medical Institute.
 * All rights reserved.
 * Use is subject to Janelia Farm Research Campus Software Copyright 1.1
 * license terms ( http://license.janelia.org/license/jfrc_copyright_1_1.html ).
 */

void set_green_color() { 
    gl_FragColor = vec4( 0, 1, 0, 1 ); 
}

// Hard coded light system, just for testing, 
// should be same as in CPU host program, for comparison
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
	float specularCoefficient = pow(nDotH, 150);
	
	vec3 specular = specularCoefficient * specular_light;
	
    

    // return diffuse + ambient + specularComponent;
    // return (0.5 * normal + vec3(0.5, 0.5, 0.5)); // normal map, for debugging
    // return reflectionVector;
    // return 0.5 * surfaceToLight + vec3(0.5, 0.5, 0.5);
    return diffuse + specular + ambient;
}
