import Foundation
import StoreKit

@MainActor
final class StoreManager: ObservableObject {
    static let shared = StoreManager()

    static let monthlyID = "layit.pro.monthly"
    static let annualID = "layit.pro.annual"
    private static let productIDs: Set<String> = [monthlyID, annualID]

    @Published private(set) var products: [Product] = []
    @Published private(set) var isPro: Bool = false

    private var transactionListener: Task<Void, Error>?

    private init() {
        isPro = UserDefaults.standard.bool(forKey: "layit_pro")
        transactionListener = listenForTransactions()
        Task { await loadProducts() }
        Task { await refreshEntitlements() }
    }

    deinit {
        transactionListener?.cancel()
    }

    // MARK: - Load Products

    func loadProducts() async {
        do {
            let storeProducts = try await Product.products(for: Self.productIDs)
            products = storeProducts.sorted { $0.price < $1.price }
        } catch {
            print("[StoreManager] Failed to load products: \(error)")
        }
    }

    func webProductPayload() -> [[String: String]] {
        products.map { product in
            [
                "id": product.id,
                "displayPrice": product.displayPrice,
                "periodLabel": Self.periodLabel(for: product)
            ]
        }
    }

    // MARK: - Purchase

    func purchase(_ productID: String) async -> Bool {
        guard let product = products.first(where: { $0.id == productID }) else {
            // Products may not be loaded yet; try loading first
            await loadProducts()
            guard let product = products.first(where: { $0.id == productID }) else {
                print("[StoreManager] Product not found: \(productID)")
                return false
            }
            return await executePurchase(product)
        }
        return await executePurchase(product)
    }

    private func executePurchase(_ product: Product) async -> Bool {
        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                let transaction = try checkVerified(verification)
                await transaction.finish()
                await refreshEntitlements()
                return isPro
            case .userCancelled:
                return false
            case .pending:
                return false
            @unknown default:
                return false
            }
        } catch {
            print("[StoreManager] Purchase failed: \(error)")
            return false
        }
    }

    // MARK: - Entitlements

    func refreshEntitlements() async {
        var hasActiveSubscription = false

        for await result in Transaction.currentEntitlements {
            if let transaction = try? checkVerified(result) {
                if Self.productIDs.contains(transaction.productID) {
                    hasActiveSubscription = true
                }
            }
        }

        setPro(hasActiveSubscription)
    }

    // MARK: - Transaction Listener

    private func listenForTransactions() -> Task<Void, Error> {
        Task.detached { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let transaction) = result {
                    await transaction.finish()
                    await self?.refreshEntitlements()
                }
            }
        }
    }

    // MARK: - Restore Purchases

    func restorePurchases() async {
        try? await AppStore.sync()
        await refreshEntitlements()
    }

    // MARK: - Helpers

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified(_, let error):
            throw error
        case .verified(let value):
            return value
        }
    }

    private func setPro(_ value: Bool) {
        isPro = value
        UserDefaults.standard.set(value, forKey: "layit_pro")
    }

    private static func periodLabel(for product: Product) -> String {
        guard let period = product.subscription?.subscriptionPeriod else { return "period" }
        let singular: String
        switch period.unit {
        case .day: singular = "day"
        case .week: singular = "week"
        case .month: singular = "month"
        case .year: singular = "year"
        @unknown default: singular = "period"
        }
        return period.value == 1 ? singular : "\(period.value) \(singular)s"
    }
}
