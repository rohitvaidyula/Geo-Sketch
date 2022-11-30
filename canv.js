// set canvas size
const canvas = document.querySelectorAll('canvas')[0]

canvas.width = window.innerWidth
canvas.height = window.innerHeight

// prepare context (drawing area of canvas)
const context = canvas.getContext('2d')
let lineWidth = 0
let isMousedown = false

// save list of points (needed for drawing but also sketch rec)
let points = []


/**
 * This function takes in an array of points and draws them onto the canvas.
 * @param {array} stroke array of points to draw on the canvas
 * @return {void}
 */
function drawOnCanvas (stroke) {
  context.strokeStyle = 'black'
  context.lineCap = 'round'
  context.lineJoin = 'round'

  const l = stroke.length - 1
  if (stroke.length >= 3) {
    const xc = (stroke[l].x + stroke[l - 1].x) / 2
    const yc = (stroke[l].y + stroke[l - 1].y) / 2
    context.lineWidth = stroke[l - 1].lineWidth
    context.quadraticCurveTo(stroke[l - 1].x, stroke[l - 1].y, xc, yc)
    context.stroke()
    context.beginPath()
    context.moveTo(xc, yc)
  } else {
    const point = stroke[l];
    context.lineWidth = point.lineWidth
    context.strokeStyle = point.color
    context.beginPath()
    context.moveTo(point.x, point.y)
    context.stroke()
  }
}

  canvas.addEventListener('pointerdown', function (e) {
    let pressure = 0.1;
    let x, y;
    let time = Date.now();
      x = e.pageX
      y = e.pageY

    isMousedown = true

    lineWidth = Math.log(pressure + 1) * 40
    context.lineWidth = lineWidth// pressure * 50;

    points.push({ x, y, time})
    drawOnCanvas(points)
  })



  canvas.addEventListener('pointermove', function (e) {
    if (!isMousedown) return
    e.preventDefault()

    let pressure = 0.1
    let x, y
    let time = Date.now();
      x = e.pageX
      y = e.pageY

    // smoothen line width
    lineWidth = (Math.log(pressure + 1) * 40 * 0.2 + lineWidth * 0.8)
    points.push({ x, y, time })

    drawOnCanvas(points);

  })



  canvas.addEventListener('pointerup', function (e) {
    let pressure = 0.1;
    let x, y;
      x = e.pageX
      y = e.pageY

    isMousedown = false


    lineWidth = 0
    
    console.log(points)
    points = []
  })