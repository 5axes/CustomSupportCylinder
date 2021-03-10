//----------------------------------------------
// Eiffel Support 
// Size must be 1x1x1 
//----------------------------------------------
$fn=40;

translate([-0.5,-0.5,-0.5]) 
difference(){
    union() {
        translate([0.5,0.5,0.0]) cylinder(h=1, r1=0.25, r2=0.25, center = true);
        translate([0.5,0.5,-0.5]) linear_extrude(height=0.6, scale=[0.3,0.3], slices=20, twist=0)
     square(1,center = true);
    }
    translate([0.5,0.5,-0.5]) rotate([90,0,0.0]) cylinder(h=1, r=0.25, center = true);
    translate([0.5,0.5,-0.5]) rotate([0,90,0.0]) cylinder(h=1, r=0.25, center = true);
}