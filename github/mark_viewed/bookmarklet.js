javascript: boxes = document.getElementsByClassName("js-reviewed-checkbox"), counter = 0;
for (let e = 0; e < boxes.length; e++) {
	    const t = boxes[e];
	    "File viewed, click, value:false" == t.dataset.gaClick && (t.click(), counter++)
}
alert("Folded " + counter);
