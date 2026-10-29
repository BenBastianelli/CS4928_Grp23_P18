package booking;

import java.util.Objects;
import java.util.Optional;

public class ComputerClassRoom extends ClassRoom {
    private final int openingHour;
    private final int closingHour;

    public ComputerClassRoom(
            String name,
            String description,
            boolean hasProjector,
            int openingHour,
            int closingHour
    ) {
        super(name, description, hasProjector);

        if (openingHour < 0 || openingHour > 23
                || closingHour < 0 || closingHour > 23
                || openingHour >= closingHour) {
            throw new IllegalArgumentException("Invalid opening or closing hours");
        }

        this.openingHour = openingHour;
        this.closingHour = closingHour;
    }

    @Override
    public Optional<Booking> book(Interval interval, User customer) {
        if (interval.getStart().getHour() < openingHour
                || interval.getEnd().getHour() > closingHour) {
            return Optional.empty();
        }

        return super.book(interval, customer);
    }

    @Override
    public boolean equals(Object o) {
        return super.equals(o)
                && openingHour == ((ComputerClassRoom) o).openingHour
                && closingHour == ((ComputerClassRoom) o).closingHour;
    }

    @Override
    public int hashCode() {
        return Objects.hash(super.hashCode(), openingHour, closingHour);
    }
}