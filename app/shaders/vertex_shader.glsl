uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec4 u_color;
attribute vec3 a_coords;
attribute vec4 a_color;
varying vec4 v_color;
void main()
{
    v_color = u_color * a_color;
    gl_Position = u_projection * u_view * u_model * vec4(a_coords,1.0);
}