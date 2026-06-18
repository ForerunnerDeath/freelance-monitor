import config
from sources import fl_ru, profi_ru
from logger import log_error


def get_orders(verbose):
    all_orders = []
    source_modules = []
    if config.ENABLE_FL_RU:
        source_modules.append(fl_ru)
    if config.ENABLE_PROFI_RU:
        source_modules.append(profi_ru)
    for source_module in source_modules:
        try:
            if source_module == fl_ru:
                pages = config.FL_RU_PAGES
            if source_module == profi_ru:
                pages = config.PROFI_RU_PAGES
            source_orders = source_module.fetch_orders(pages=pages, verbose=verbose)
        except Exception as error:
            log_error(f"Ошибка получения заказов из {source_module.__name__}: {error}")
            continue
        if verbose:
            print("Источник", source_module.__name__, "вернул", len(source_orders), "заказов")
        all_orders.extend(source_orders)
    return all_orders