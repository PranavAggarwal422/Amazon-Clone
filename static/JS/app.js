// Resizing select search categories container dynamically 
const select = document.getElementById('category-select');
const searchInput = document.querySelector(".nav-search-text input"); 
const searchBar = document.querySelector(".search-bar") ;
const navSearch = document.querySelector(".nav-search") ;

function resizeSelect() {
    const temp = document.createElement('span');

    temp.style.visibility = 'hidden';
    temp.style.position = 'absolute';

    temp.style.fontSize = window.getComputedStyle(select).fontSize;
    temp.style.fontFamily = window.getComputedStyle(select).fontFamily;
    temp.innerText = select.options[select.selectedIndex].text; // to get Actual Text shown instead of backend value

    document.body.appendChild(temp);
    select.style.width = (temp.offsetWidth + 35) + 'px'; // extra space for arrow

    let max_size = navSearch.offsetWidth * 35/100 ;

    if(temp.offsetWidth + 35 > max_size){
        select.style.width = max_size + "px"; 
    }
    document.body.removeChild(temp);
  }

if(searchInput) { 
select.addEventListener('change', resizeSelect);
window.addEventListener('load', resizeSelect);
window.addEventListener("resize" , resizeSelect) ; 
searchInput.addEventListener("focus" , () => { 
    searchBar.classList.add("active-focus") ; 
})

searchInput.addEventListener("blur" , () => { 
    searchBar.classList.remove("active-focus"); 
})

// applying backdrop when searchInput in focus 
const overlay = document.querySelector(".overlay") ; 


function showOverlay() { 
    console.log("hello") ; 
    overlay.style.display = "block" ; 
    document.body.style.overflow = "hidden" ; 
}
function hideOverlay() { 
    overlay.style.display = "none" ; 
    document.body.style.overflow = "auto"  ; 
}

searchInput.addEventListener("focus" , showOverlay) ; 
searchInput.addEventListener("blur" , hideOverlay) ; 
}

// Deciding number of li to shown according to screen width  
let navShop = document.querySelector(".nav-shop") ; 
let allShopLi = document.querySelectorAll(".nav-shop-li"); 

function adjustNavItems() { 
    let right = navShop.getBoundingClientRect().right ; 
    let executed = false ; 
    for(let shopLi of allShopLi){
        shopLi.style.display = "inline-block" ; 
        let shopLiRight = shopLi.getBoundingClientRect().right ; 
        if(shopLiRight > right || executed){
            shopLi.style.display = "none" ; 
            executed = true ; 
        }
    }
}
if(navShop){
    window.addEventListener("load" , adjustNavItems) ; 
    window.addEventListener("resize" , adjustNavItems) ;
}

// Deciding margin-top of shopping row 
let shoppingRow = document.querySelector(".shopping .row") ; 
let carouselSection = document.querySelector(".carousel-section"); 

function giveRowMargin() { 
    let height = carouselSection.getBoundingClientRect().height ; 
    let marginTop = (height-250)*(-1) -20 ; 
    shoppingRow.style.marginTop = marginTop + "px"; 
}

if (carouselSection) {
    window.addEventListener("load" , giveRowMargin) ; 
    window.addEventListener("resize" , giveRowMargin) ; 
}

// seeAll and seeLess Logic 
let seeAllBtns = document.querySelectorAll(".see-all-btn");
let seeLessBtns = document.querySelectorAll(".see-less-btn");

seeAllBtns.forEach((seeAllBtn) => {
    seeAllBtn.addEventListener("click", () => {
        seeAllBtn.style.display = "none";
        let hiddenList = seeAllBtn.parentElement.parentElement.querySelectorAll("ul")[1];
        hiddenList.style.height = hiddenList.scrollHeight + "px";
    });
});

seeLessBtns.forEach((seeLessBtn) => {
    seeLessBtn.addEventListener("click", () => {
        let hiddenList = seeLessBtn.parentElement;
        hiddenList.style.height = "0px";

        // After transition, show the See All button again
        let seeAllBtn = hiddenList.parentElement.querySelector(".see-all-btn");
        
        if(seeAllBtn.classList[0] == "offcanvas-seeAll") { 
            setTimeout(() => {
                seeAllBtn.style.display = "flex";
            }, 400); // Match transition duration
        }
        else{
            seeAllBtn.style.display = "flex";
        }
    });
});

// filter-panel
let FilterInputs = document.querySelectorAll(".filter-panel input")

FilterInputs.forEach((FilterInput) => { 
    FilterInput.addEventListener("click" , ()=> { 
        if(FilterInput.nextSibling.style.fontWeight == 400 ||FilterInput.nextSibling.style.fontWeight == "" ){
            FilterInput.nextSibling.style.fontWeight = 700 ; 
        }
        else { 
            FilterInput.nextSibling.style.fontWeight = 400 ; 
        }
    })
})

// registration-form 
let RegisterInputs = document.querySelectorAll(".registration-form input") ; 
RegisterInputs.forEach((RegisterInput) => { 
    RegisterInput.classList.add("form-control") ; 
} )