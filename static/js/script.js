document.addEventListener("DOMContentLoaded", function () {



    /*
    ==========================
    금리 기간 변경
    ==========================
    */


    const buttons =
        document.querySelectorAll(".rate-period-btn");


    const rates =
        document.querySelectorAll(".rate-value");


    const changes =
        document.querySelectorAll(".change-value");


    const title =
        document.getElementById("periodTitle");



    const periodName = {


        "1m":"1개월 금리",

        "3m":"3개월 금리",

        "6m":"6개월 금리",

        "12m":"12개월 금리",

        "24m":"24개월 금리",

        "36m":"36개월 금리"


    };





    function formatChange(value){


        let num =
            Number(value);



        if(
            isNaN(num) ||
            num === 0
        ){

            return "-";

        }



        if(num > 0){


            return `
            <span class="text-primary">
            +${num.toFixed(2)}%
            </span>
            `;


        }
        else{


            return `
            <span class="text-danger">
            ▲${Math.abs(num).toFixed(2)}%
            </span>
            `;


        }


    }







    buttons.forEach(btn=>{


        btn.addEventListener(
            "click",
            function(){



                let period =
                    this.dataset.period;



                buttons.forEach(b=>{

                    b.classList.remove(
                        "active"
                    );

                });



                this.classList.add(
                    "active"
                );



                if(title){

                    title.innerText =
                    periodName[period];

                }






                // 금리 변경

                rates.forEach(cell=>{


                    let value =
                    cell.dataset[period];



                    if(
                        value &&
                        value !== "null"
                    ){


                        cell.innerText =
                        Number(value)
                        .toFixed(2)
                        + "%";


                    }
                    else{


                        cell.innerText =
                        "-";


                    }


                });






                // 변동 변경

                changes.forEach(cell=>{


                    let value =
                    cell.dataset[
                        "change-" + period
                    ];



                    cell.innerHTML =
                    formatChange(value);



                });



            }

        );


    });












    /*
    ==========================
    검색 기능
    ==========================
    */


    const searchInput =
        document.getElementById(
            "searchInput"
        );



    if(searchInput){


        searchInput.addEventListener(
            "input",
            function(){



                let keyword =
                    this.value
                    .toLowerCase()
                    .trim();



                document
                .querySelectorAll(
                    ".rate-row"
                )
                .forEach(row=>{


                    let text =
                    row.innerText
                    .toLowerCase();



                    if(
                        text.includes(keyword)
                        ||
                        keyword === ""
                    ){

                        row.style.display="";

                    }
                    else{

                        row.style.display="none";

                    }


                });



            }

        );


    }












    /*
    ==========================
    금리 변동 필터
    ==========================
    */


    const filterButtons =
        document.querySelectorAll(
            ".change-filter"
        );



    filterButtons.forEach(btn=>{


        btn.addEventListener(
            "click",
            function(){



                let filter =
                    this.dataset.filter;



                filterButtons.forEach(b=>{

                    b.classList.remove(
                        "active"
                    );

                });



                this.classList.add(
                    "active"
                );





                document
                .querySelectorAll(
                    ".rate-row"
                )
                .forEach(row=>{



                    let change =
                    Number(
                        row.dataset.change
                    );



                    if(filter==="all"){


                        row.style.display="";


                    }


                    else if(
                        filter==="up"
                    ){


                        row.style.display =
                        change > 0
                        ? ""
                        : "none";


                    }


                    else if(
                        filter==="down"
                    ){


                        row.style.display =
                        change < 0
                        ? ""
                        : "none";


                    }


                    else if(
                        filter==="same"
                    ){


                        row.style.display =
                        change === 0
                        ? ""
                        : "none";


                    }



                });



            }

        );


    });












    /*
    ==========================
    금리 업데이트
    ==========================
    */


    const updateBtn =
        document.getElementById(
            "updateBtn"
        );


    const updateMessage =
        document.getElementById(
            "updateMessage"
        );




    if(updateBtn){



        updateBtn.addEventListener(
            "click",
            function(){



                updateBtn.disabled =
                true;



                updateBtn.innerText =
                "⏳ 업데이트 중...";



                if(updateMessage){


                    updateMessage.innerText =
                    "최신 금리 데이터를 가져오는 중입니다.";


                }




                fetch("/update_rates")

                .then(response=>
                    response.json()
                )


                .then(data=>{



                    if(
                        data.status==="success"
                    ){


                        if(updateMessage){


                            updateMessage.innerText =
                            "✅ 금리 업데이트 완료";


                        }



                        setTimeout(()=>{


                            location.reload();


                        },1500);



                    }
                    else{


                        if(updateMessage){


                            updateMessage.innerText =
                            "❌ 오류 : "
                            + data.message;


                        }


                        updateBtn.disabled =
                        false;


                    }



                })



                .catch(error=>{


                    if(updateMessage){


                        updateMessage.innerText =
                        "❌ 연결 오류";


                    }


                    updateBtn.disabled =
                    false;


                });



            }

        );


    }




});