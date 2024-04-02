javascript: boxes = document.getElementsByClassName("js-reviewed-checkbox"), counter = 0;
for (let e = 0; e < boxes.length; e++) {
	    const t = boxes[e];
	    !t.hasAttribute("checked") && (t.click(), counter++)
}
alert("Folded " + counter);
