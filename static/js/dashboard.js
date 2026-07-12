/* ===================================
   SBRateBot V4 Dashboard JS
   Full Replacement Version
=================================== */


let productData = [];

let selectedCategory = "정기예금";

let selectedPeriod = "12개월";

let aiTimer = null;



document.addEventListener(
    "DOMContentLoaded",
    function(){


        console.log(
            "SBRateBot V4 Dashboard Loaded"
        );


        initDashboard();

        initProductFilter();

        initProductSearch();

        initAISearch();

        initAIAutoSearch();


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
        await fetch(
            "/api/kpi"
        );


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



// ===================================
// 우리금융 Market Position
// ===================================

async function loadWoori(){


    try{


        const response =
        await fetch(
            "/api/woori"
        );


        const data =
        await response.json();



        setText(
            "#woori-rate",
            Number(data.rate || 0).toFixed(2) + "%"
        );



        setText(
            "#market-rank",
            data.market_rank + "위"
        );



        setText(
            "#basis-product",
            data.basis_product || "-"
        );



        setText(
            "#basis-product-card",
            data.basis_product || "-"
        );



        setText(
            "#current-rate",
            Number(data.rate || 0).toFixed(2) + "%"
        );



        // 아래 3개는 HTML 색상 표시 필요하므로 setHTML 유지

        setHTML(
            "#average-gap",
            formatGap(
                data.average_gap
            )
        );


        setHTML(
            "#highest-gap",
            formatGap(
                data.highest_gap
            )
        );


        setHTML(
            "#lowest-gap",
            formatGap(
                data.lowest_gap
            )
        );


    }
    catch(error){


        console.error(
            "WOORI ERROR",
            error
        );


    }


}




// ===================================
// 증감 표시
// ===================================

function formatGap(value){

    let num =
        Number(value || 0);


    if(num > 0){

        return "+" +
            num.toFixed(2)
            + "%";

    }


    if(num < 0){

        return num.toFixed(2)
            + "%";

    }


    return "0.00%";

}



/* ===================================
   금융지주 비교
=================================== */


async function loadFinancial(){


    try{


        const response =
        await fetch(
            "/api/financial"
        );


        const data =
        await response.json();



        // 기존 금융지주 비교표 유지
        renderRateTable(
            "#financial-table",
            data
        );



        // ===================================
        // 4대 금융 순위 표시
        // ===================================


        const financialList = data.filter(
            function(item){


                const bank =
                String(
                    item.bank || ""
                );


                return (

                    bank.includes("우리금융")

                    ||

                    bank.includes("신한")

                    ||

                    bank.includes("하나")

                    ||

                    bank.includes("KB")

                );


            }
        );



        financialList.sort(
            function(a,b){


                return Number(b.rate)
                -
                Number(a.rate);


            }
        );



        const wooriRank =
        financialList.findIndex(
            function(item){


                return String(
                    item.bank || ""
                )
                .includes(
                    "우리금융"
                );


            }
        );



        if(
            wooriRank >= 0
        ){


            setText(
                "#financial-rank",
                (wooriRank + 1)
                +
                "위 / "
                +
                financialList.length
                +
                "개사"
            );


        }
        else{


            setText(
                "#financial-rank",
                "-"
            );


        }



    }
    catch(error){


        console.error(
            "FINANCIAL ERROR",
            error
        );


    }


}



/* ===================================
   시장 TOP10
=================================== */


async function loadRates(){


    try{


        const response =
        await fetch(
            "/api/rates"
        );


        const data =
        await response.json();


        renderRateTable(
            "#market-table",
            data
        );


    }
    catch(error){


        console.error(
            "RATE ERROR",
            error
        );


    }


}



/* ===================================
   공통 금리 테이블
=================================== */


function renderRateTable(
    selector,
    data
){


    const table =
    document.querySelector(
        selector
    );


    if(!table)
        return;


    table.innerHTML = "";


    if(
        !data ||
        data.length === 0
    ){


        table.innerHTML = `

        <tr>

        <td colspan="5">
        데이터가 없습니다.
        </td>

        </tr>

        `;


        return;

    }


    data.forEach(
        function(item,index){


            const row =
            document.createElement(
                "tr"
            );


            const rank =
            item.rank ||
            index + 1;


            let rankClass = "";


            if(rank === 1){

                rankClass = "top1";

            }
            else if(rank === 2){

                rankClass = "top2";

            }
            else if(rank === 3){

                rankClass = "top3";

            }


            let bankName =
            item.bank || "";


            if(
                bankName.includes(
                    "우리금융"
                )
            ){

                bankName =
                `<strong>${bankName}</strong>`;

            }


            row.innerHTML = `

            <td class="${rankClass}">
            ${rank}위
            </td>

            <td>
            ${bankName}
            </td>

            <td>
            ${item.product || ""}
            </td>

            <td>
            <strong>
            ${Number(
                item.rate || 0
            ).toFixed(2)}%
            </strong>
            </td>

            <td>
            ${formatChange(
                item.change
            )}
            </td>

            `;


            table.appendChild(
                row
            );


        }
    );


}



/* ===================================
   전체 상품 조회
=================================== */


async function loadProducts(){


    try{


        const response =
        await fetch(
            "/api/products"
        );


        productData =
        await response.json();


        renderProducts();


    }
    catch(error){


        console.error(
            "PRODUCT ERROR",
            error
        );


    }


}



function renderProducts(){


    const table =
    document.querySelector(
        "#product-table"
    );


    if(!table)
        return;


    const keyword =
    (
        document.querySelector(
            "#product-search"
        )?.value
        ||
        ""
    )
    .toLowerCase();


    let filtered =
    productData.filter(
        function(item){


            const category =
            item.category || "";


            const period =
            item.period || "";


            const bank =
            String(
                item.bank || ""
            )
            .toLowerCase();


            const product =
            String(
                item.product || ""
            )
            .toLowerCase();


            return (

                category === selectedCategory

                &&

                (
                    selectedCategory !== "정기예금"

                    ||

                    period === selectedPeriod
                )

                &&

                (
                    bank.includes(keyword)

                    ||

                    product.includes(keyword)
                )

            );


        }
    );


    filtered.sort(
        function(a,b){


            return (
                Number(b.rate)
                -
                Number(a.rate)
            );


        }
    );


    table.innerHTML = "";


    if(filtered.length === 0){


        table.innerHTML = `

        <tr>

        <td colspan="5">
        조회 결과가 없습니다.
        </td>

        </tr>

        `;


        return;

    }


    filtered.forEach(
        function(item,index){


            const row =
            document.createElement(
                "tr"
            );


            const rank =
            index + 1;


            let rankClass = "";


            if(rank === 1){

                rankClass = "top1";

            }
            else if(rank === 2){

                rankClass = "top2";

            }
            else if(rank === 3){

                rankClass = "top3";

            }


            let bankName =
            item.bank || "";


            if(
                bankName.includes(
                    "우리금융"
                )
            ){

                bankName =
                `<strong>${bankName}</strong>`;

            }


            row.innerHTML = `

            <td class="${rankClass}">
            ${rank}위
            </td>

            <td>
            ${bankName}
            </td>

            <td>
            ${item.product || ""}
            </td>

            <td>
            <strong>
            ${Number(
                item.rate || 0
            ).toFixed(2)}%
            </strong>
            </td>

            <td>
            ${formatChange(
                item.change
            )}
            </td>

            `;


            table.appendChild(
                row
            );


        }
    );


}



/* ===================================
   상품 탭 / 기간
=================================== */


function initProductFilter(){


    const categoryButtons =
    document.querySelectorAll(
        ".product-tabs button"
    );


    const periodButtons =
    document.querySelectorAll(
        ".period-filter button"
    );


    categoryButtons.forEach(
        function(button){


            button.addEventListener(
                "click",
                function(){


                    categoryButtons.forEach(
                        function(item){

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    button.classList.add(
                        "active"
                    );


                    selectedCategory =
                    button.innerText.trim();


                    renderProducts();


                }
            );


        }
    );


    periodButtons.forEach(
        function(button){


            button.addEventListener(
                "click",
                function(){


                    periodButtons.forEach(
                        function(item){

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    button.classList.add(
                        "active"
                    );


                    selectedPeriod =
                    button.innerText.trim();


                    renderProducts();


                }
            );


        }
    );


}



/* ===================================
   상품 검색
=================================== */


function initProductSearch(){


    const input =
    document.querySelector(
        "#product-search"
    );


    if(!input)
        return;


    input.addEventListener(
        "input",
        renderProducts
    );


}



/* ===================================
   AI Summary
=================================== */


async function loadAI(){


    try{


        const response =
        await fetch(
            "/api/ai"
        );


        const data =
        await response.json();


        const box =
        document.querySelector(
            "#ai-summary"
        );


        if(!box)
            return;


        box.innerHTML = `

        <ul>

        ${
            (data.summary || [])
            .map(
                function(item){

                    return `<li>${item}</li>`;

                }
            )
            .join("")
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
   AI 검색 초기화
=================================== */


function initAISearch(){


    const input =
    document.querySelector(
        "#ai-question"
    );


    const button =
    document.querySelector(
        "#ai-search-btn"
    );


    if(button){


        button.addEventListener(
            "click",
            searchAI
        );


    }


    if(input){


        input.addEventListener(
            "keydown",
            function(event){


                if(event.key === "Enter"){


                    event.preventDefault();


                    clearTimeout(
                        aiTimer
                    );


                    searchAI();


                }


            }
        );


    }


}



/* ===================================
   AI 자동 검색
=================================== */


function initAIAutoSearch(){


    const input =
    document.querySelector(
        "#ai-question"
    );


    if(!input)
        return;


    input.addEventListener(
        "input",
        function(){


            clearTimeout(
                aiTimer
            );


            aiTimer =
            setTimeout(
                function(){


                    if(
                        input.value.trim().length >= 2
                    ){


                        searchAI();


                    }


                },
                800
            );


        }
    );


}



/* ===================================
   AI 검색
=================================== */


async function searchAI(){


    const input =
    document.querySelector(
        "#ai-question"
    );


    const answer =
    document.querySelector(
        "#ai-answer"
    );


    if(!input || !answer)
        return;


    const question =
    input.value.trim();


    if(!question){


        answer.innerText =
        "질문을 입력해주세요.";


        return;

    }


    answer.innerText =
    "검색중입니다...";


    try{


        const response =
        await fetch(
            "/api/ai/search",
            {

                method: "POST",

                headers: {

                    "Content-Type":
                    "application/json"

                },

                body:
                JSON.stringify({

                    question: question

                })

            }
        );


        const data =
        await response.json();


        answer.innerText =
        data.answer ||
        "검색 결과가 없습니다.";


    }
    catch(error){


        console.error(
            "AI SEARCH ERROR",
            error
        );


        answer.innerText =
        "검색 오류가 발생했습니다.";


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



function setHTML(
    selector,
    value
){


    const element =
    document.querySelector(
        selector
    );


    if(element){


        element.innerHTML =
        value;


    }


}



function formatGap(value){


    const number =
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



function formatChange(value){


    if(
        value === null
        ||
        value === undefined
        ||
        value === "-"
    ){


        return "-";


    }


    const number =
    Number(
        String(value)
        .replace("+","")
    );


    if(isNaN(number)){


        return value;


    }


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