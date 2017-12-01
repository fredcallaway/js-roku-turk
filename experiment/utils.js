module.exports = {
  sleep(seconds) { 
    return new Promise(resolve => {
      setTimeout(() => {
        resolve();
      }, seconds * 1000);
    });
  }
}
