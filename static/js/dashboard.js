/* ===================================
   SBRateBot V4 Dashboard JS
=================================== */


document.addEventListener(
    "DOMContentLoaded",
    function(){

        console.log(
            "SBRateBot V4 Dashboard Loaded"
        );

        initDashboard();

    }
);





async function initDashboard(){


    await loadKPI();

    await loadWoori();

    await loadFinancial();

    await loadRates();

    await loadProducts();

    await loadAI();


}








/* ===================================
   KPI
=================================== */


async function loadKPI(){


    try{


        const response =
        await fetch("/api/kpi");


        const data =
        await response.json();



        setText(
            "#product-count",
            data.product_count + "개"
        );


        setText(
            "#max-rate",
            data.max_rate
        );


        setText(
            "#avg-rate",
            data.average_rate
        );


        setText(
            "#min-rate",
            data.min_rate
        );


    }


    catch(error){

        console.error(
            "KPI ERROR",
            error
        );

    }


}








/* ===================================
   우리금융 Market Position
=================================== */


async function loadWoori(){


    try{


        const response =
        await fetch("/api/woori");


        const data =
        await response.json();



        setText(
            "#market-rank",
            data.market_rank + "위"
        );


        setText(
            "#financial-rank",
            data.financial_rank + "위"
        );


        setText(
            "#woori-rate",
            data.rate.toFixed(2) + "%"
        );



        document.querySelector(
            "#average-gap"
        ).innerHTML =
        formatGap(
            data.average_gap
        );



        document.querySelector(
            "#highest-gap"
        ).innerHTML =
        formatGap(
            data.highest_gap
        );



        document.querySelector(
            "#lowest-gap"
        ).innerHTML =
        formatGap(
            data.lowest_gap
        );



    }


    catch(error){

        console.error(
            "WOORI ERROR",
            error
        );

    }


}









/* ===================================
   금융지주 비교
=================================== */


async function loadFinancial(){


    try{


        const response =
        await fetch("/api/financial");


        const data =
        await response.json();



        const table =
        document.querySelector(
            "#financial-table"
        );


        if(!table) return;



        table.innerHTML="";



        data.forEach(item=>{


            const row =
            document.createElement("tr");


            row.innerHTML = `

            <td>
                ${item.rank}위
            </td>

            <td>
                ${item.bank}
            </td>

            <td>
                ${item.product}
            </td>

            <td>
                ${item.rate.toFixed(2)}%
            </td>

            <td>
                ${formatChange(item.change)}
            </td>

            `;


            table.appendChild(row);


        });



    }


    catch(error){

        console.error(
            "FINANCIAL ERROR",
            error
        );

    }


}









/* ===================================
   Market TOP10
=================================== */


async function loadRates(){


    try{


        const response =
        await fetch("/api/rates");


        const data =
        await response.json();



        const table =
        document.querySelector(
            "#market-table"
        );



        if(!table) return;



        table.innerHTML="";



        data.forEach(item=>{


            const row =
            document.createElement("tr");



            row.innerHTML = `


            <td>
                ${item.rank}
            </td>


            <td>
                ${item.bank}
            </td>


            <td>
                ${item.product}
            </td>


            <td>
                ${item.rate.toFixed(2)}%
            </td>


            <td>
                ${formatChange(item.change)}
            </td>


            `;


            table.appendChild(row);


        });



    }


    catch(error){


        console.error(
            "RATE ERROR",
            error
        );


    }


}









/* ===================================
   전체 상품조회
=================================== */


async function loadProducts(){


    try{


        const response =
        await fetch("/api/products");


        const data =
        await response.json();



        const table =
        document.querySelector(
            "#product-table"
        );



        if(!table) return;



        table.innerHTML="";



        data.forEach(item=>{


            const row =
            document.createElement("tr");



            row.innerHTML = `


            <td>
                ${item.bank}
            </td>


            <td>
                ${item.product}
            </td>


            <td>
                ${item.rate.toFixed(2)}%
            </td>


            <td>
                ${formatChange(item.change)}
            </td>


            `;


            table.appendChild(row);


        });



    }


    catch(error){

        console.error(
            "PRODUCT ERROR",
            error
        );

    }


}









/* ===================================
   AI Summary
=================================== */


async function loadAI(){


    try{


        const response =
        await fetch("/api/ai");


        const data =
        await response.json();



        const box =
        document.querySelector(
            "#ai-summary"
        );



        if(!box) return;



        box.innerHTML = `


        <ul>

        ${
            data.summary.map(
                item =>
                `<li>${item}</li>`
            ).join("")
        }

        </ul>


        `;



    }


    catch(error){

        console.error(
            "AI ERROR",
            error
        );

    }


}









/* ===================================
   공통 함수
=================================== */


function setText(
    selector,
    value
){

    const element =
    document.querySelector(
        selector
    );


    if(element){

        element.innerText =
        value;

    }

}








// Market Position 대비 표시

function formatGap(value){


    let number =
    Number(value);



    if(number > 0){


        return `

        <span class="rate-change increase">

        +${number.toFixed(2)}%p

        </span>

        `;


    }



    if(number < 0){


        return `

        <span class="rate-change decrease">

        ▲${Math.abs(number).toFixed(2)}%p

        </span>

        `;


    }



    return "0.00%p";


}








// 일반 전일대비

function formatChange(value){


    if(
        !value ||
        value === "-"
    ){

        return "-";

    }



    let number =
    parseFloat(value);



    if(number > 0){


        return `

        <span class="rate-change increase">

        +${number.toFixed(2)}%

        </span>

        `;


    }



    if(number < 0){


        return `

        <span class="rate-change decrease">

        ▲${Math.abs(number).toFixed(2)}%

        </span>

        `;


    }



    return "0.00%";


}