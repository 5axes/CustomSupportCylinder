//----------------------------------------------
// T Support 
// Size must height = 1 mm 
//----------------------------------------------
$fn=60;

translate([-0.5,-0.5,-0.5]) 
union() {
    translate([0.5,0.5,0.0]) cylinder( h=1, r=0.5 , center = true);
    translate([1,0.5,0.5]) rotate([-90, 0, 90]) {
			linear_extrude(height=1) {
				polygon(points=[[-1.5,0],[-1.5,-0.01],[1.5,-0.01],[1.5,0],[-1.5,0],[1.5,0],[0.1,0.5],[-0.1,0.5]], convexity=1);
			}        
    }
}
