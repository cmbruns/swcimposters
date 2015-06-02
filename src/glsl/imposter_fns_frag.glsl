#version 120

void set_green_color() { 
    gl_FragColor = vec4( 0, 1, 0, 1 ); 
}

// Hard coded light system, should be same as in CPU host program, for comparison
vec3 light_rig(vec4 pos, vec3 normal, vec3 surface_color) {
    const vec3 ambient_light = vec3(0.2, 0.2, 0.2);
    const vec3 diffuse_light = vec3(0.8, 0.8, 0.8);
    const vec3 specular_light = vec3(0.8, 0.8, 0.8);
    const vec3 light_pos = vec3(-5, 3, 3); 
    // const vec3 surface_color = vec3(1, 0.5, 1);

	vec3 surfaceToLight = normalize(light_pos); //  - (pos / pos.w).xyz);
	
	float diffuseCoefficient = max(0.0, dot(normal, surfaceToLight));
	vec3 diffuse = diffuseCoefficient * surface_color * diffuse_light;

    vec3 ambient = ambient_light * surface_color;
    
    vec3 incidenceVector = -surfaceToLight; //a unit vector
	vec3 reflectionVector = reflect(incidenceVector, normal); //also a unit vector
	vec3 cameraPosition = vec3(0,0,0);
	vec3 surfaceToCamera = normalize(cameraPosition - pos.xyz); //also a unit vector
	float cosAngle = max(0.0, dot(surfaceToCamera, reflectionVector));
	float specularCoefficient = pow(cosAngle, 150);
	
	vec3 specular = specularCoefficient * specular_light;
    

    // return diffuse + ambient + specularComponent;
    // return 0.5 * normal + vec3(0.5, 0.5, 0.5);
    // return 0.5 * surfaceToLight + vec3(0.5, 0.5, 0.5);
    return ambient + diffuse + specular;
}
