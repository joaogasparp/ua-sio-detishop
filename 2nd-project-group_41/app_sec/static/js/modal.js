var myModal = document.getElementById('modal')
var myInput = document.getElementById('myInput')

myModal.addEventListener('shown.bs.modal', function () {
    console.log("paulo")
  myInput.focus()
})
