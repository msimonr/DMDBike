function displayFecha(date){
    return new Date(date).getDay() + '/'+ (new Date(date).getMonth()+1) + '/' + new Date(date).getFullYear()
}

function displayDistanceText(km){
    km_updt = Math.round(km * 10000) / 10000; //Redondeado a 4 digitos
    if(km_updt < 1){
        return String(Math.round(km_updt* 1000)) +' m'; // 0.734 km -> 734 m
    }
    return km_updt.toFixed(2) + ' km';
}

async function actualizar() {
    try {
        const res = await fetch('/stats');
        const data = await res.json();
        const kmNum = Math.round(data.km * 10000) / 10000;
        const kmSesion = Math.round(data.km_sesion * 10000) / 10000;
        document.getElementById('km').textContent = displayDistanceText(kmNum)
        document.getElementById('km_sesion').textContent = displayDistanceText(kmSesion)
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
            <div>
            <strong>${data.nombre || ""}</strong><br>
            ${data.foto ? `<img src="${data.foto}" style="width:80px;height:80px;object-fit:cover;border-radius:6px;margin-top:4px;">` : ""}<br>
            ${displayDistanceText(data.km)}<br>
            <small>${displayFecha(data.creado_en)}</small><br>
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
      li.innerHTML = `
        <strong>${idx + 1}.</strong> 
        ${item.nombre || 'Sin nombre'} – ${Number(item.km).toFixed(2)} km
        <small style="display:block;opacity:.6;">${displayFecha(item.creado_en)}</small>
      `;
      ul.appendChild(li);
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