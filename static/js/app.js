const metas = [14.11, 141.1, 1411];

function displayFecha(date){
    return new Date(date).getDay() + '/'+ (new Date(date).getMonth()+1) + '/' + new Date(date).getFullYear()
}

function displayDistanceText(km){
    km_updt = Math.round(km * 10000) / 10000; //Redondeado a 4 digitos
    if(km_updt < 1){
        return [String(Math.round(km_updt* 1000)) , 'm']; // 0.734 km -> 734 m
    }
    return [km_updt.toFixed(1), 'km'];
}

function actualizarBarraProgreso(actual, metasArray) {
  const fill = document.getElementById("progress-fill");
  if (!fill || !metasArray || metasArray.length === 0) return;

  // metasArray = [14, 141, 1411]
  const [m1, m2, m3] = metasArray;
  const tramoAncho = 100 / metasArray.length;  // 3 metas => 33.333...% cada tramo
  let porcentaje = 0;

  if (actual <= m1) {
    // estamos en el 1er tramo
    porcentaje = (actual / m1) * tramoAncho;
  } else if (actual <= m2) {
    // 2do tramo: ya tenemos 1 tramo completo + la parte del 2do
    const avanceTramo = (actual - m1) / (m2 - m1); // 0..1
    porcentaje = tramoAncho + avanceTramo * tramoAncho;
  } else {
    // 3er tramo (hasta m3)
    const avanceTramo = (actual - m2) / (m3 - m2); // 0..1
    porcentaje = tramoAncho * 2 + avanceTramo * tramoAncho;
  }

  // no pasarse
  porcentaje = Math.min(porcentaje, 100);
  fill.style.width = porcentaje + "%";

  // actualizar etiquetas debajo si existen
  metasArray.forEach((meta, idx) => {
    const label = document.getElementById(`label-${idx + 1}`);
    if (label) label.textContent = meta + " km";
  });
}


async function actualizar() {
    try {
        const res = await fetch('/stats');
        const data = await res.json();
        const kmNum = Math.round(data.km * 10000) / 10000;
        const kmSesion = Math.round(data.km_sesion * 10000) / 10000;
        kmTotal = document.getElementById('km');
        kmTotal_viejo = document.getElementById('km').textContent;
        kmTotal.textContent = displayDistanceText(kmNum)[0]
        document.getElementById('kmUnit').textContent = displayDistanceText(kmNum)[1];
        document.getElementById('km_sesion').textContent = '🚴‍♂️ ' + displayDistanceText(kmSesion)[0] + ' ' + displayDistanceText(kmSesion)[1];

        //Animaciones
        actualizarBarraProgreso(kmNum, metas);
        if(kmTotal_viejo !== kmTotal.textContent){
          kmTotal.classList.remove("km-updated"); 
          void kmTotal.offsetWidth;               
          kmTotal.classList.add("km-updated");
          }
    } catch (e) {
        console.log("Error al actualizar", e);
    }
}


async function actualizarSesionRandom() {
    try {
        const res = await fetch('/random_session');
        const data = await res.json();
    if (!data.ok) return;
        const cont = document.getElementById('random-sesion');
        cont.innerHTML = `
            <div class="sesion">
                <span class="sesion-name">${data.nombre || ""}</span>
                ${data.foto 
                  ? `<img src="${data.foto}" class="sesion-img">`
                  : `<img src="/static/default.png" class="sesion-img">`
                  }
                <span class="sesion-distance"><span class="sesion-sumo">Sumó</span> ${displayDistanceText(data.km)[0] + ' '+ displayDistanceText(data.km)[1]}</span>
                <span class="sesion-date">${displayFecha(data.creado_en)}</span>
            </div>
        `;
    } catch (e) {
        console.log("Error obteniendo sesión random", e);
    }
}


async function actualizarTop10() {
  try {
    const res = await fetch('/top_10');
    const data = await res.json();
    if (!data.ok) return;

    const ul = document.getElementById('top10-list');
    ul.innerHTML = ''; // limpio lo anterior

    data.top10.forEach((item, idx) => {

      const li = document.createElement('li');

      if(item.nombre){
        li.innerHTML = `
                <span class="number-top">${idx + 1}.</span>
                <span class="name-top"> ${item.nombre}</span>
                <span class="distance-top">${displayDistanceText(item.km)[0] + ' ' +displayDistanceText(item.km)[1]}</span>
                <span class="date-top">${displayFecha(item.creado_en)}</span>
        `;
        li.classList.add("top-entry");
        ul.appendChild(li);
        }
    });

  } catch (err) {
    console.log('Error al traer top10', err);
  }
}


// PARA RENOVAR
setInterval(actualizar, 1000);
setInterval(actualizarSesionRandom, 5000);
setInterval(actualizarTop10, 15000);


// AL CARGAR
actualizarSesionRandom();
actualizarTop10();