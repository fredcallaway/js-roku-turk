function sleep(seconds) { 
  return new Promise(resolve => {
    setTimeout(() => {
      resolve();
    }, seconds * 1000);
  });
}

// showdown.setOption('smartIndentationFix', true)
var converter = new showdown.Converter();
function markdown(txt) {
  // Remove leading spaces so as not to interpret indented
  // blocks as code blocks. Use fenced code blocks instead.
  txt = txt.replace(/^[ ]+/gm, '')
  return converter.makeHtml(txt);
};
