from fastapi import APIRouter
from .endpoints import scraping, comprehend, deidentify

router = APIRouter()
router.include_router(scraping.router, tags=["Scraping"])
router.include_router(comprehend.router, tags=["Comprehend"])
router.include_router(deidentify.router, tags=["MaskORAnonymize"])
# router.include_router(prices.router, tags=["Prices"])
