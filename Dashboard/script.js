

const delay = 10000 // interval in ms

function advancement() {
  const advancementValue = document.getElementById('advancementValue')
  let interval;

  if (interval === undefined) {
    interval = setInterval(async () => {
      // const response = await fetch('http://127.0.0.1:8080/advancement', {
      const response = await fetch('http://127.0.0.1:8000/advancement', {
        method: 'GET'
      })
      const data = (await response.json())
      advancementValue.innerHTML = `${data.progress}%`
    }, delay);
  }
}

function position() {
  const positionValue = document.getElementById('positionValue')
  let interval;

  if (interval === undefined) {
    interval = setInterval(async () => {
      const response = await fetch('http://127.0.0.1:8000/position', {
        method: 'GET'
      })
      const data = (await response.json())
      ///x en "" ou pas ? wtf
      positionValue.innerHTML = `X : ${data.x} | Y: ${data.y}, | Z : ${data.z}`
    }, delay);
  }
}

async function commandPost() {
  // e.preventDefault()
  const commandInput = document.getElementById('commandList')

  let url = "http://127.0.0.1:8000/cmd";
  let xhr = new XMLHttpRequest();
  xhr.open("POST", url);
  xhr.setRequestHeader("Accept", "application/json");
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      console.log((xhr.responseText).log);
    }
  };

  let data = {
    command: commandInput.value
  };
  // let data = commandInput.value
  console.log("data" + data)
  const response = xhr.send(JSON.stringify(data));
  //const response = xhr.send(String(data));
}

// handle file 
const fileinput = document.getElementById('fileinput')
const url = "http://127.0.0.1:8000/uploadGcode"
const fileform = document.getElementById('fileForm')
const currentfile = document.getElementById('currentFile')
fileform.addEventListener('change', async (e) => {
  const files = document.querySelector('[name=file]').files;
  currentfile.innerHTML = files[0].name
})
fileform.addEventListener('submit', async (e) => {
  const files = document.querySelector('[name=file]').files;
  // disable default action
  e.preventDefault();

  console.log(files)
  const formData = new FormData();
  formData.append('file', files[0]); //gcode ??? c le file ?? why binary ? 

  // post form data
  const xhr = new XMLHttpRequest();
  xhr.responseType = 'json';

  // log response
  xhr.onload = () => {
    console.log(xhr.response);
  };
  // create and send the reqeust
  xhr.open('POST', url);
  xhr.send(await formData);
});

// handle command
const commandBtn = document.getElementById('commandBtn')
commandBtn.onclick = commandPost


// handle progress
const advancementBtn = document.getElementById('advancementBtn')
advancementBtn.onclick = advancement


// handle position
const positionBtn = document.getElementById('positionBtn')
positionBtn.onclick = position


